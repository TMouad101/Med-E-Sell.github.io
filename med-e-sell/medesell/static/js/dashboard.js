
const btns= document.querySelectorAll("#sidebar-wrapper a");
const sections = document.querySelectorAll(".section");

function show (panelIndex){
    sections.forEach(function(node){
        node.style.display = "none";
    })
    sections[panelIndex].style.display = "block";
}
show(0);


function show_message(other_id, product_id){
    const parent_div0 = document.querySelector('.parent0');
    parent_div0.innerHTML = `<form action="/chat/`+ other_id +`/`+ product_id +`" method="POST" class="container_fluid">
    <div class="text-muted d-flex justify-content-start align-items-center p-3 mt-2 border rounded">
        <input type="text" name="message" class="form-control form-control-lg" id="exampleFormControlInput2"
        placeholder="Type message" />
        <input type="submit" class="btn btn-primary" value="Send">         
        </div>
      </form>`
    const parent_div = document.getElementById('parent');
    parent_div.innerHTML = '';
    const product_div = document.getElementById('product_div')
    product_div.innerHTML = ''
    fetch('http://127.0.0.1:5000/show/'+other_id+'-'+product_id)
  .then(response => response.json())
  .then(data => {
        
        data.forEach(message => {
          product_child = `<div class="col text-center ">
                              <img class="" src="../../static/uploads/`+ message['product_photo'] +`" alt="" style="width: 80px;">
                          </div>
                          <div class="col text-center   align-items-center justify-content-center">
                              <p class="fw-bold">`+ message['product_name'] +`</p>
                              <p>` + message['product_desc'] + `</p>
                          </div>
                          <div class="col text-center  d-flex align-items-center justify-content-center">
                              <a href="/products/`+ product_id +`" > Product <i class="fa fa-arrow-right"></i> </a>
                          </div>`
          product_div.innerHTML = product_child
            if(message['receiver_id'] == other_id){
                child_div = `<div class="d-flex flex-row justify-content-end ">
                                      <div>
                                        <p class="small p-2 me-3 mb-1 text-white rounded-3 bg-primary">`+ message['content']+`</p>
                                        <p class="small me-3 mb-3 rounded-3 text-muted">`+message['timestamp']+`</p>
                                      </div>
                                      <p class="fw-bold p-2">`+message['sender_name']+`</p>
                                    </div>`
            }else{
                child_div = `<div class="d-flex flex-row justify-content-start ">
                <p class="fw-bold p-2">`+message['sender_name']+`</p>
              <div>
                <p class="small p-2 ms-3 mb-1 rounded-3" style="background-color: #f5f6f7;">`+ message['content']+`</p>
                <p class="small ms-3 mb-3 rounded-3 text-muted float-end">`+message['timestamp']+`</p>
              </div>
            </div>`
            }
            var childDiv = document.createElement('div');
            childDiv.innerHTML = child_div;
            parent_div.appendChild(childDiv);
        })
    // Handle the API response data here
    console.log(data);
    })
  .catch(error => {
    // Handle any errors that occurred during the request
    console.error('Error:', error);
  });



}
