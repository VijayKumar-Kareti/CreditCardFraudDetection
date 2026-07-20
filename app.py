from flask import (
    Flask,
    render_template,
    request,
    send_file,
    redirect,
    url_for
)
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from datetime import datetime
from io import BytesIO
from flask import send_file
from openpyxl import Workbook
import pandas as pd
import joblib
import io
import time
import math
from flask import send_file


import os

REPORT_FOLDER = "reports"
os.makedirs(REPORT_FOLDER, exist_ok=True)

app = Flask(__name__)

# ===============================
# Load Model & Scaler
# ===============================

model = joblib.load("models/fraud_detection_model.pkl")
scaler = joblib.load("models/scaler.pkl")


# Store latest CSV result
LAST_RESULT = None
LAST_RESULT_CSV = None


# ===============================
# Home Page
# ===============================

@app.route("/")
def home():
    return render_template("index.html")


# ===============================
# Single Transaction Prediction
# ===============================

@app.route("/predict_single", methods=["POST"])
def predict_single():

    try:

        feature_names = (
            ["Time"]
            + [f"V{i}" for i in range(1, 29)]
            + ["Amount"]
        )

        values = []

        for feature in feature_names:
            values.append(float(request.form[feature]))

        transaction = pd.DataFrame(
            [values],
            columns=feature_names
        )

        transaction[["Time", "Amount"]] = scaler.transform(
            transaction[["Time", "Amount"]]
        )

        prediction = model.predict(transaction)[0]
        probability = model.predict_proba(transaction)[0]

        confidence = round(max(probability) * 100, 2)

        if prediction == 1:
            result = "Fraudulent Transaction"
        else:
            result = "Normal Transaction"

        return render_template(
            "index.html",
            prediction=result,
            confidence=confidence
        )

    except Exception as e:

        return render_template(
            "index.html",
            error=str(e)
        )


# ===============================
# CSV Prediction
# ===============================

@app.route("/predict_csv", methods=["POST"])
def predict_csv():

    global LAST_RESULT, LAST_RESULT_CSV

    try:

        file = request.files["csv_file"]
        filename = file.filename

        start_time = time.time()

        if file.filename == "":
            return render_template(
                "index.html",
                error="Please choose a CSV file."
            )

        df = pd.read_csv(file)

        # Remove Class column if present
        if "Class" in df.columns:
            df = df.drop(columns=["Class"])

        required_columns = (
            ["Time"]
            + [f"V{i}" for i in range(1, 29)]
            + ["Amount"]
        )

        if list(df.columns) != required_columns:

            return render_template(
                "index.html",
                error="CSV format is incorrect."
            )

        # Scale Time & Amount
        df[["Time", "Amount"]] = scaler.transform(
            df[["Time", "Amount"]]
        )

        predictions = model.predict(df)
        probabilities = model.predict_proba(df)

        labels = []
        confidence = []

        for pred, prob in zip(predictions, probabilities):

            if pred == 1:
                labels.append("Fraud")
            else:
                labels.append("Normal")

            confidence.append(
                round(max(prob) * 100, 2)
            )

        result_df = df.copy()

        result_df["Prediction"] = labels
        result_df["Confidence (%)"] = confidence

        # Dashboard Statistics
        total = len(result_df)
        normal = (result_df["Prediction"] == "Normal").sum()
        fraud = (result_df["Prediction"] == "Fraud").sum()
        fraud_rate = round((fraud / total) * 100, 2) if total else 0
        normal_rate = round((normal / total) * 100, 2) if total else 0
       
        # ==========================
        # Pagination Settings
        # ==========================

        

        
        # Store CSV for download
        LAST_RESULT = result_df.copy()

        csv_buffer = io.StringIO()

        result_df.to_csv(
            csv_buffer,
            index=False
        )

        LAST_RESULT_CSV = csv_buffer.getvalue()

        # Cleaner table for UI
        display_df = pd.DataFrame({
            "Transaction ID": range(1, total + 1),
            "Prediction": labels,
            "Confidence (%)": confidence
        })
        
       

        # ==========================
        # Show only first 400 rows
        # ==========================

        

        csv_table = display_df.to_html(
            classes="prediction-table",
            index=False,
            table_id="predictionTable"
     )
        end_time = time.time()

        prediction_time = round(end_time - start_time, 2)

        return render_template(
            "index.html",
            csv_table=csv_table,
            total=total,
            normal=normal,
            fraud=fraud,
            fraud_rate=fraud_rate,
            normal_rate=normal_rate,
            prediction_time=prediction_time,
            accuracy=99.94
     )

    except Exception as e:

        return render_template(
            "index.html",
            error=str(e)
        )


# ===============================
# Download Prediction CSV
# ===============================
@app.route("/download_excel")
def download_excel():

    global LAST_RESULT

    if LAST_RESULT is None:
        return "No prediction results available."

    wb = Workbook()
    ws = wb.active
    ws.title = "Prediction Results"

    # Header
    ws.append(LAST_RESULT.columns.tolist())

    # Data
    for row in LAST_RESULT.itertuples(index=False):
        ws.append(list(row))

    output = BytesIO()
    wb.save(output)
    output.seek(0)

    return send_file(
        output,
        as_attachment=True,
        download_name="prediction_results.xlsx",
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
@app.route("/download_pdf")
def download_pdf():

    global LAST_RESULT

    if LAST_RESULT is None:
        return "No prediction available."

    pdf_path = os.path.join(REPORT_FOLDER, "Fraud_Report.pdf")

    doc = SimpleDocTemplate(pdf_path)

    styles = getSampleStyleSheet()

    elements = []

    title = Paragraph(
        "<b><font size=18>Credit Card Fraud Detection Report</font></b>",
        styles["Title"]
    )

    elements.append(title)
    elements.append(Paragraph("<br/>", styles["Normal"]))

    elements.append(
        Paragraph(
            f"<b>Date:</b> {datetime.now().strftime('%d-%m-%Y %H:%M:%S')}",
            styles["Normal"]
        )
    )

    elements.append(Paragraph("<br/>", styles["Normal"]))

    total = len(LAST_RESULT)

    normal = (LAST_RESULT["Prediction"] == "Normal").sum()

    fraud = (LAST_RESULT["Prediction"] == "Fraud").sum()

    fraud_rate = round((fraud / total) * 100, 2)

    data = [
        ["Metric", "Value"],
        ["Total Transactions", total],
        ["Normal Transactions", normal],
        ["Fraud Transactions", fraud],
        ["Fraud Rate", f"{fraud_rate}%"],
        ["Model Accuracy", "99.94%"]
    ]

    table = Table(data, colWidths=[3 * inch, 2 * inch])

    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.darkblue),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("GRID", (0, 0), (-1, -1), 1, colors.black),
        ("BACKGROUND", (0, 1), (-1, -1), colors.beige),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
    ]))

    elements.append(table)

    elements.append(Paragraph("<br/><br/>", styles["Normal"]))

    elements.append(
        Paragraph(
            "This report was automatically generated by the Credit Card Fraud Detection Dashboard.",
            styles["Normal"]
        )
    )

    doc.build(elements)

    return send_file(pdf_path, as_attachment=True)


# ===============================
# Run App
# ===============================




@app.route("/download_sample_csv")
def download_sample_csv():
    sample_file = os.path.join(
        app.root_path,
        "sample_data",
        "sample_transactions.csv"
    )

    return send_file(
        sample_file,
        as_attachment=True,
        download_name="sample_transactions.csv"
    )


if __name__ == "__main__":
    app.run(debug=True)