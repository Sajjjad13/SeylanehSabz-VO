function calc(){

    let total = 0;

    document.querySelectorAll(".qty-input").forEach(input => {

        let qty = Number(input.value || 0);
        let price = Number(input.dataset.price || 0);

        total += qty * price;

    });

    document.getElementById("total").innerText =
        total.toLocaleString();

    let target = Number(document.getElementById("target").innerText || 0);

    let diff = target - total;

    let diffBox = document.getElementById("diff");

    if(total >= target){
        diffBox.innerHTML = "تارگت پوشش داده شد";
        diffBox.className = "diff green";
    } else {
        diffBox.innerHTML = "اختلاف: " + diff.toLocaleString();
        diffBox.className = "diff red";
    }
}


function clearAll(){
    document.querySelectorAll(".qty-input").forEach(i => i.value = 0);
    calc();
}


function submitOrder(){

    let items = [];
    let total = 0;

    document.querySelectorAll(".qty-input").forEach(input => {

        let qty = Number(input.value || 0);

        if(qty > 0){

            let price = Number(input.dataset.price);
            let title = input.dataset.title;

            items.push({ title, qty, price });

            total += qty * price;
        }

    });

    fetch("/submit", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({ items, total })
    })
    .then(res => res.json())
    .then(data => {
        alert("ثبت شد. جمع کل: " + data.total.toLocaleString());
    });

}