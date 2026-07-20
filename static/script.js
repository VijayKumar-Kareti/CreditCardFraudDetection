// ==============================
// Toggle Transaction Form
// ==============================

function toggleForm() {

    const form = document.getElementById("transactionForm");

    form.classList.toggle("hidden");

}


// ==============================
// Sample Normal Transaction
// ==============================

function fillNormal() {

    const values = [
        0,
        -1.359807,
        -0.072781,
        2.536347,
        1.378155,
        -0.338321,
        0.462388,
        0.239599,
        0.098698,
        0.363787,
        0.090794,
        -0.551600,
        -0.617801,
        -0.991390,
        -0.311169,
        1.468177,
        -0.470401,
        0.207971,
        0.025791,
        0.403993,
        0.251412,
        -0.018307,
        0.277838,
        -0.110474,
        0.066928,
        0.128539,
        -0.189115,
        0.133558,
        -0.021053,
        149.62
    ];

    fillForm(values);

}


// ==============================
// Sample Fraud Transaction
// ==============================

function fillFraud() {

    const values = [
        406,
        -2.312227,
        1.951992,
        -1.609851,
        3.997906,
        -0.522188,
        -1.426545,
        -2.537387,
        1.391657,
        -2.770089,
        -2.772272,
        3.202033,
        -2.899907,
        -0.595222,
        -4.289254,
        0.389724,
        -1.140747,
        -2.830056,
        -0.016822,
        0.416956,
        0.126911,
        0.517232,
        -0.035049,
        -0.465211,
        0.320198,
        0.044519,
        0.177840,
        0.261145,
        -0.143276,
        0.00
    ];

    fillForm(values);

}


// ==============================
// Fill Form Function
// ==============================

function fillForm(values) {

    const inputs = document.querySelectorAll(
        "#transactionForm input"
    );

    inputs.forEach((input, index) => {

        input.value = values[index];

    });

}
function showLoader(){

    document.getElementById("loader").classList.remove("hidden");

}
function printDashboard() {
    window.print();
}
// ===============================
// Table Pagination
// ===============================

document.addEventListener("DOMContentLoaded", function () {

    const table = document.querySelector(".prediction-table");

    if (!table) return;

    const rows = table.querySelectorAll("tbody tr");

    const rowsPerPage = 400;

    let currentPage = 1;

    const totalRows = rows.length;

    const totalPages = Math.ceil(totalRows / rowsPerPage);

    const prevBtn = document.getElementById("prevBtn");
    const nextBtn = document.getElementById("nextBtn");
    const pageInfo = document.getElementById("pageInfo");

    function showPage(page) {

        rows.forEach(row => row.style.display = "none");

        const start = (page - 1) * rowsPerPage;
        const end = Math.min(start + rowsPerPage, totalRows);

        for (let i = start; i < end; i++) {
            rows[i].style.display = "";
        }

        pageInfo.innerHTML =
            `Showing ${start + 1}-${end} of ${totalRows} transactions | Page ${page} of ${totalPages}`;

        prevBtn.disabled = page === 1;
        nextBtn.disabled = page === totalPages;
    }

    prevBtn.addEventListener("click", function () {
        if (currentPage > 1) {
            currentPage--;
            showPage(currentPage);
        }
    });

    nextBtn.addEventListener("click", function () {
        if (currentPage < totalPages) {
            currentPage++;
            showPage(currentPage);
        }
    });

    showPage(currentPage);

});
// ===============================
// Search & Filter
// ===============================

document.addEventListener("DOMContentLoaded", function () {

    const searchInput = document.getElementById("searchInput");
    const filterSelect = document.getElementById("filterSelect");
    const table = document.querySelector(".prediction-table");

    if (!table) return;

    const rows = table.querySelectorAll("tbody tr");

    function filterTable() {

        const searchText = searchInput.value.toLowerCase().trim();
        const filterValue = filterSelect.value;

        rows.forEach(row => {

            const text = row.innerText.toLowerCase();

            const prediction =
                row.cells[1].innerText.trim();

            const matchesSearch =
                text.includes(searchText);

            const matchesFilter =
                filterValue === "all" ||
                prediction === filterValue;

            if (matchesSearch && matchesFilter) {
                row.style.display = "";
            } else {
                row.style.display = "none";
            }

        });

    }

    searchInput.addEventListener("keyup", filterTable);

    filterSelect.addEventListener("change", filterTable);

});