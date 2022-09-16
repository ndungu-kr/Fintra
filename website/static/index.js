function deleteTransaction(transactionId) {
    fetch("/delete-transaction", {
        method: "POST",
        body: JSON.stringify({ transactionId: transactionId }),
    }).then((_res) => {
        window.location.href = "/";
    });
}