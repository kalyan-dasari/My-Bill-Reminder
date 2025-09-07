document.addEventListener('DOMContentLoaded', function() {
    const itemTypeSelect = document.getElementById('itemType');
    const addItemForm = document.getElementById('addItemForm');

    function updateForm() {
        const selectedType = itemTypeSelect.value;
        let formHTML = '';

        if (selectedType === 'recharge') {
            formHTML = `
                <input type="hidden" name="type" value="recharge">
                <div class="mb-3">
                    <label for="contactName" class="form-label">Contact Name</label>
                    <input type="text" class="form-control" id="contactName" name="contact_name" required>
                </div>
                <div class="mb-3">
                    <label for="rechargeDate" class="form-label">Recharge Date</label>
                    <input type="date" class="form-control" id="rechargeDate" name="recharge_date" required>
                </div>
                <div class="mb-3">
                    <label for="validDays" class="form-label">Valid Days</label>
                    <input type="number" class="form-control" id="validDays" name="valid_days" required>
                </div>
                <div class="mb-3">
                    <label for="planAmount" class="form-label">Plan Amount</label>
                    <input type="number" step="0.01" class="form-control" id="planAmount" name="plan_amount" required>
                </div>
            `;
        } else if (selectedType === 'emi') {
            formHTML = `
                <input type="hidden" name="type" value="emi">
                <div class="mb-3">
                    <label for="emiName" class="form-label">EMI Name</label>
                    <input type="text" class="form-control" id="emiName" name="emi_name" required>
                </div>
                <div class="mb-3">
                    <label for="dueDate" class="form-label">Due Date</label>
                    <input type="date" class="form-control" id="dueDate" name="due_date" required>
                </div>
                <div class="mb-3">
                    <label for="amount" class="form-label">Amount</label>
                    <input type="number" step="0.01" class="form-control" id="amount" name="amount" required>
                </div>
            `;
        } else if (selectedType === 'event') {
            formHTML = `
                <input type="hidden" name="type" value="event">
                <div class="mb-3">
                    <label for="eventName" class="form-label">Event Name</label>
                    <input type="text" class="form-control" id="eventName" name="event_name" required>
                </div>
                <div class="mb-3">
                    <label for="eventDate" class="form-label">Date</label>
                    <input type="date" class="form-control" id="eventDate" name="event_date" required>
                </div>
                <div class="mb-3">
                    <label for="notes" class="form-label">Notes</label>
                    <textarea class="form-control" id="notes" name="notes"></textarea>
                </div>
            `;
        } else if (selectedType === 'monthly_bill') {
            formHTML = `
                <input type="hidden" name="type" value="monthly_bill">
                <div class="mb-3">
                    <label for="billName" class="form-label">Bill Name</label>
                    <input type="text" class="form-control" id="billName" name="bill_name" required>
                </div>
                <div class="mb-3">
                    <label for="amount" class="form-label">Amount</label>
                    <input type="number" step="0.01" class="form-control" id="amount" name="amount" required>
                </div>
                <div class="mb-3">
                    <label for="dueDate" class="form-label">Due Date</label>
                    <input type="date" class="form-control" id="dueDate" name="due_date" required>
                </div>
            `;
        } else if (selectedType === 'custom_bill') {
            formHTML = `
                <input type="hidden" name="type" value="custom_bill">
                <div class="mb-3">
                    <label for="billName" class="form-label">Bill Name</label>
                    <input type="text" class="form-control" id="billName" name="bill_name" required>
                </div>
                <div class="mb-3">
                    <label for="billType" class="form-label">Type (e.g., Wi-Fi)</label>
                    <input type="text" class="form-control" id="billType" name="bill_type" required>
                </div>
                <div class="mb-3">
                    <label for="dueDate" class="form-label">Due Date</label>
                    <input type="date" class="form-control" id="dueDate" name="due_date" required>
                </div>
                <div class="mb-3">
                    <label for="amount" class="form-label">Amount</label>
                    <input type="number" step="0.01" class="form-control" id="amount" name="amount" required>
                </div>
            `;
        }
        addItemForm.innerHTML = formHTML;
        addItemForm.action = `/add/${selectedType}`;
    }

    itemTypeSelect.addEventListener('change', updateForm);

    const openModalBtn = document.getElementById('openModalBtn');
    openModalBtn.addEventListener('click', function() {
        updateForm();
    });

    // Handle Edit Modal
    const editModal = document.getElementById('editModal');
    editModal.addEventListener('show.bs.modal', function (event) {
        const button = event.relatedTarget;
        const itemId = button.getAttribute('data-id');
        const itemType = button.getAttribute('data-type');
        const modalTitle = editModal.querySelector('.modal-title');
        const modalBody = editModal.querySelector('.modal-body form');

        modalTitle.textContent = `Edit ${itemType.charAt(0).toUpperCase() + itemType.slice(1)} Item`;
        modalBody.action = `/edit/${itemType}/${itemId}`;

        // Fetch data and populate form
        fetch(`/get_item/${itemType}/${itemId}`)
            .then(response => response.json())
            .then(data => {
                let formHTML = '';
                if (itemType === 'recharge') {
                    formHTML = `
                        <div class="mb-3">
                            <label for="editContactName" class="form-label">Contact Name</label>
                            <input type="text" class="form-control" id="editContactName" name="contact_name" value="${data.contact_name}" required>
                        </div>
                        <div class="mb-3">
                            <label for="editRechargeDate" class="form-label">Recharge Date</label>
                            <input type="date" class="form-control" id="editRechargeDate" name="recharge_date" value="${data.recharge_date}" required>
                        </div>
                        <div class="mb-3">
                            <label for="editValidDays" class="form-label">Valid Days</label>
                            <input type="number" class="form-control" id="editValidDays" name="valid_days" value="${data.valid_days}" required>
                        </div>
                        <div class="mb-3">
                            <label for="editPlanAmount" class="form-label">Plan Amount</label>
                            <input type="number" step="0.01" class="form-control" id="editPlanAmount" name="plan_amount" value="${data.plan_amount}" required>
                        </div>
                    `;
                } else if (itemType === 'emi') {
                    formHTML = `
                        <div class="mb-3">
                            <label for="editEmiName" class="form-label">EMI Name</label>
                            <input type="text" class="form-control" id="editEmiName" name="emi_name" value="${data.emi_name}" required>
                        </div>
                        <div class="mb-3">
                            <label for="editDueDate" class="form-label">Due Date</label>
                            <input type="date" class="form-control" id="editDueDate" name="due_date" value="${data.due_date}" required>
                        </div>
                        <div class="mb-3">
                            <label for="editAmount" class="form-label">Amount</label>
                            <input type="number" step="0.01" class="form-control" id="editAmount" name="amount" value="${data.amount}" required>
                        </div>
                    `;
                } else if (itemType === 'event') {
                    formHTML = `
                        <div class="mb-3">
                            <label for="editEventName" class="form-label">Event Name</label>
                            <input type="text" class="form-control" id="editEventName" name="event_name" value="${data.event_name}" required>
                        </div>
                        <div class="mb-3">
                            <label for="editEventDate" class="form-label">Date</label>
                            <input type="date" class="form-control" id="editEventDate" name="event_date" value="${data.event_date}" required>
                        </div>
                        <div class="mb-3">
                            <label for="editNotes" class="form-label">Notes</label>
                            <textarea class="form-control" id="editNotes" name="notes">${data.notes || ''}</textarea>
                        </div>
                    `;
                } else if (itemType === 'monthly') {
                    formHTML = `
                        <div class="mb-3">
                            <label for="editBillName" class="form-label">Bill Name</label>
                            <input type="text" class="form-control" id="editBillName" name="bill_name" value="${data.bill_name}" required>
                        </div>
                        <div class="mb-3">
                            <label for="editAmount" class="form-label">Amount</label>
                            <input type="number" step="0.01" class="form-control" id="editAmount" name="amount" value="${data.amount}" required>
                        </div>
                        <div class="mb-3">
                            <label for="editDueDate" class="form-label">Due Date</label>
                            <input type="date" class="form-control" id="editDueDate" name="due_date" value="${data.due_date}" required>
                        </div>
                    `;
                } else if (itemType === 'custom') {
                    formHTML = `
                        <div class="mb-3">
                            <label for="editBillName" class="form-label">Bill Name</label>
                            <input type="text" class="form-control" id="editBillName" name="bill_name" value="${data.bill_name}" required>
                        </div>
                        <div class="mb-3">
                            <label for="editBillType" class="form-label">Type (e.g., Wi-Fi)</label>
                            <input type="text" class="form-control" id="editBillType" name="bill_type" value="${data.bill_type}" required>
                        </div>
                        <div class="mb-3">
                            <label for="editDueDate" class="form-label">Due Date</label>
                            <input type="date" class="form-control" id="editDueDate" name="due_date" value="${data.due_date}" required>
                        </div>
                        <div class="mb-3">
                            <label for="editAmount" class="form-label">Amount</label>
                            <input type="number" step="0.01" class="form-control" id="editAmount" name="amount" value="${data.amount}" required>
                        </div>
                    `;
                }
                modalBody.innerHTML = formHTML;
            });
    });

    // Initial form update on page load
    updateForm();
});