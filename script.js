const API_URL = "https://finora-money-manager.onrender.com";

Those **must not be inside a `.js` file**. That's why the Save code isn't running.

Let's clean this properly.

### Replace the ENTIRE `script.js`

Delete everything currently inside `script.js` and paste **only this**:

:::writing{variant="standard" id="74216" title="FINORA clean script.js"}
```javascript
const API_URL = "https://finora-money-manager.onrender.com";

// ===============================
// TRANSACTION MODAL
// ===============================

const transactionModal = document.getElementById("transactionModal");
const closeModal = document.getElementById("closeModal");
const openModalButtons = document.querySelectorAll(".open-modal");

openModalButtons.forEach(function (button) {
    button.addEventListener("click", function () {
        if (transactionModal) {
            transactionModal.classList.add("show");
        }
    });
});

if (closeModal) {
    closeModal.addEventListener("click", function () {
        transactionModal.classList.remove("show");
    });
}

if (transactionModal) {
    transactionModal.addEventListener("click", function (event) {
        if (event.target === transactionModal) {
            transactionModal.classList.remove("show");
        }
    });
}


// ===============================
// SAVE TRANSACTION
// ===============================

const transactionForm = document.getElementById("transactionForm");

if (transactionForm) {
    transactionForm.addEventListener("submit", async function (event) {

        event.preventDefault();

        const type = document.getElementById("transactionType").value;
        const category = document.getElementById("transactionCategory").value;
        const amount = document.getElementById("transactionAmount").value;

        const userId = localStorage.getItem("finora_user_id");

        if (!userId) {
            alert("User not found. Please login again.");
            return;
        }

        if (!category || !amount) {
            alert("Please enter category and amount.");
            return;
        }

        try {

            const response = await fetch(
                API_URL + "/transactions?user_id=" + userId,
                {
                    method: "POST",

                    headers: {
                        "Content-Type": "application/json"
                    },

                    body: JSON.stringify({
                        transaction_type: type,
                        category: category,
                        amount: Number(amount)
                    })
                }
            );

            const data = await response.json();

            if (!response.ok) {
                alert(data.detail || "Transaction could not be saved.");
                return;
            }

            alert("Transaction saved successfully! 💰");

            transactionForm.reset();

            if (transactionModal) {
                transactionModal.classList.remove("show");
            }

        } catch (error) {

            alert(
                "Could not connect to FINORA backend.\n\n" +
                "Please make sure FastAPI is running."
            );
        }
    });
}