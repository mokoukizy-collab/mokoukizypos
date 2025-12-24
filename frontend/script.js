const API_BASE_URL = typeof window.API_BASE_URL === "string" ? window.API_BASE_URL : location.origin;
const grid = document.getElementById("grid");
const modal = document.getElementById("modal");
const modalClose = document.getElementById("modalClose");
const modalImg = document.getElementById("modalImg");
const modalName = document.getElementById("modalName");
const modalPrice = document.getElementById("modalPrice");
const modalDesc = document.getElementById("modalDesc");
const modalBuy = document.getElementById("modalBuy");
let allProducts = [];
function fmtPrice(p, c){return new Intl.NumberFormat("zh-Hant", {style:"currency", currency:c||"TWD"}).format(p||0)}
function render(products){
  grid.innerHTML = "";
  for(const p of products){
    const card = document.createElement("a");
    card.className = "card";
    card.href = p.product_url || "#";
    card.target = p.product_url ? "_blank" : "_self";
    const img = document.createElement("div");
    img.className = "card-img";
    img.innerHTML = `<img src="${p.image_url || ""}" alt="" referrerpolicy="no-referrer">`;
    const body = document.createElement("div");
    body.className = "card-body";
    const name = document.createElement("h3");
    name.className = "card-name";
    name.textContent = p.name;
    const price = document.createElement("div");
    price.className = "card-price";
    price.textContent = fmtPrice(p.price, p.currency);
    body.appendChild(name);
    body.appendChild(price);
    card.appendChild(img);
    card.appendChild(body);
    card.addEventListener("click", e=>{
      if(!p.product_url){e.preventDefault();openModal(p)}
    });
    grid.appendChild(card);
  }
}
function openModal(p){
  modalImg.referrerPolicy = "no-referrer";
  modalImg.src = p.image_url || "";
  modalName.textContent = p.name;
  modalPrice.textContent = fmtPrice(p.price, p.currency);
  modalDesc.textContent = p.description || "";
  modalBuy.href = p.product_url || "#";
  modal.classList.add("show");
}
function closeModal(){modal.classList.remove("show")}
modalClose.addEventListener("click", closeModal);
modal.addEventListener("click", e=>{if(e.target.classList.contains("modal-backdrop")) closeModal()});
async function fetchProducts(){
  try{
    const r = await fetch(`${API_BASE_URL}/api/config`);
    const data = await r.json();
    const menu = Array.isArray(data.menu) ? data.menu : [];
    allProducts = menu.map(m=>({id:0, name:m.name, price:m.price, currency:"TWD", description:"menu", image_url:""}));
  }catch(e){
    allProducts = [];
  }
  render(allProducts);
}
for(const el of document.querySelectorAll(".filter")){
  el.addEventListener("click", ()=>{
    document.querySelectorAll(".filter").forEach(b=>b.classList.remove("active"));
    el.classList.add("active");
    const type = el.getAttribute("data-filter");
    render(type==="all"?allProducts:allProducts.filter(p=>(p.description||"").includes(type)));
  });
}
fetchProducts().catch(()=>{});
