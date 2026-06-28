
function calc(){

    let total = 0;

    document.querySelectorAll(".qty-input").forEach(input => {

        let qty = Number(input.value || 0);
        let price = Number(input.dataset.price || 0);

        total += qty * price;

    });

    document.getElementById("total").innerText =
        total.toLocaleString();

    let targetText = document.getElementById("target").innerText || "0";
    let target = Number(targetText.replace(/,/g, ''));

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

    document.querySelectorAll(".qty-input").forEach(i => {
        i.value = 0;
    });

    calc();
}


function submitOrder(){

    let items = [];
    let total = 0;

    document.querySelectorAll(".qty-input").forEach(input => {

        let qty = Number(input.value || 0);

        if(qty > 0){

            let price = Number(input.dataset.price || 0);
            let title = input.dataset.title;

            items.push({
                title: title,
                qty: qty,
                price: price,
                total: qty * price
            });

            total += qty * price;
        }

    });

    if(items.length === 0){
        alert("هیچ محصولی انتخاب نشده");
        return;
    }

    fetch("/submit", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            customer: "{{customer}}",
            items: items,
            total: total
        })
    })
    .then(res => res.json())
    .then(data => {

        if(data.status !== "ok"){
            alert("خطا در ثبت سفارش");
            return;
        }

        // ذخیره کل سفارش برای step3
        sessionStorage.setItem("orderResult", JSON.stringify(data));

        // رفتن به صفحه خلاصه سفارش
        window.location.href = "/summary";

    })
    .catch(err => {

        console.log(err);
        alert("خطا در ارتباط با سرور");

    });

}