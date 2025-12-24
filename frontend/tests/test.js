function write(msg){const el=document.getElementById("results");const p=document.createElement("div");p.textContent=msg;el.appendChild(p)}
function assert(cond,msg){if(!cond)throw new Error(msg)}
try{
  assert(typeof fmtPrice==="function","fmtPrice missing");
  const s=fmtPrice(100,"TWD");
  assert(typeof s==="string","fmtPrice output");
  write("fmtPrice ok");
  const p={name:"X",price:100,currency:"TWD",description:"",image_url:"",product_url:""};
  openModal(p);
  assert(document.getElementById("modal").classList.contains("show"),"modal open");
  closeModal();
  assert(!document.getElementById("modal").classList.contains("show"),"modal close");
  write("modal open/close ok");
  write("All tests passed");
}catch(e){write("Test failed: "+e.message)}
