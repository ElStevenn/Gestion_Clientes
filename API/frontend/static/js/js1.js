let ip_api = "185.254.206.129"; // Change when API is deployed on the server
let api_key = "rmpxCixzGRet81UnltZUBLdURHhnJy4QSltELa6HjU8="; // Your API key if needed
let datos_totales = []; // Stores all data loaded from the WebSocket
let maxInnerArrayLength = 30; // Max number of rows per page
let reconnectInterval = 1000; // Time to wait before attempting reconnect (1 second)
let pagina_actual = 1; // Initialize the current page to 1


function setupWebSocket() {
  let socket = new WebSocket(`ws://${ip_api}/ws_tabla`);

  socket.onopen = function(e) {
    console.log("[open] Connection established");
    socket.send('get_data'); // Request the data from the server
  };

  socket.onmessage = function(event) {
    console.log(`[message] Data received from server: ${event.data}`);
    datos_totales = JSON.parse(event.data); // Parse the received data and store it
  
    let currentPage = obtenerNumeroDePagina(); // Get the current page number
    let currentPageData = reshapeArray(datos_totales, maxInnerArrayLength)[currentPage - 1];
    buildTable(currentPageData);
    actualizarBotonesDePaginacion(); 
  };
  

  socket.onclose = function(event) {
    if (event.wasClean) {
      console.log(`[close] Connection closed cleanly, code=${event.code}, reason=${event.reason}`);
    } else {
      console.error('[close] Connection died, attempting to reconnect');
      setTimeout(setupWebSocket, reconnectInterval);
    }
  };

  socket.onerror = function(error) {
    console.error(`[error] ${error.message}`);
  };
}

// Function to get the current page number from the URL
function obtenerNumeroDePagina() {
  const urlParams = new URLSearchParams(window.location.search);
  const pagina = urlParams.get('pag');
  return pagina ? parseInt(pagina) : 1;
}

// Function to build the table with the data for the current page
function buildTable(datos_pagina) {
  let tbody = document.getElementById('tbody_usuarios');
  
  let rows = "";
  datos_pagina.forEach(function(usuario) {
    rows += "<tr>";
    rows += `<td><input type="text" value="${usuario.nombre}" class="editable"></td>`;
    rows += `<td><input type="text" value="${usuario.apellidos}" class="editable"></td>`;
    rows += `<td><input type="text" value="${usuario.numero_telefono}" class="editable"></td>`;
    rows += `<td><input type="text" value="${usuario.codigo_postal}" class="editable"></td>`;
    rows += `<td><input type="text" value="${usuario.url_registro}" class="editable"></td>`;
    rows += `<td><input type="text" value="${usuario.otra_info || ''}" class="editable"></td>`;
    rows += `<td><input type="text" value="${usuario.estado || ''}" class="editable"></td>`;
    rows += `<td><input type="text" value="${usuario.respuesta || ''}" class="editable"></td>`;
    rows += `<td><input type="text" value="${usuario.columa_adicional || ''}" class="editable"></td>`; // Este campo está desabilitado, pero en sí está habilitado en el código
    rows += "</tr>";
  });

  tbody.innerHTML = rows;
}

// Function to reshape the array into chunks for pagination
function reshapeArray(array, maxInnerArrayLength) {
  if (!Array.isArray(array)) {
    throw new TypeError('The first argument must be an array.');
  }

  const result = [];
  for (let i = 0; i < array.length; i += maxInnerArrayLength) {
    result.push(array.slice(i, i + maxInnerArrayLength));
  }
  return result;
}

// Modify cambiarPagina to interact with WebSocket and update table
function cambiarPagina(nuevaPagina) {
  pagina_actual = nuevaPagina; // Update the current page number
  let currentPageData = reshapeArray(datos_totales, maxInnerArrayLength)[pagina_actual - 1];
  buildTable(currentPageData);
  actualizarBotonesDePaginacion();
}

function actualizarBotonesDePaginacion() {
  let totalPaginas = Math.ceil(datos_totales.length / maxInnerArrayLength);
  let container = document.getElementById('pagination');
  container.innerHTML = ''; // Clear existing buttons

  // Add "previous" button if not on the first page
  if (pagina_actual > 1) {
    let prevButton = crearBotonDePagina(pagina_actual - 1, '«');
    container.appendChild(prevButton);
  }

  // Add buttons for all pages
  for (let i = 1; i <= totalPaginas; i++) {
    let pageButton = crearBotonDePagina(i, i.toString());
    if (i === pagina_actual) {
      pageButton.classList.add('active'); // Highlight the current page button
    }
    container.appendChild(pageButton);
  }

  // Add "next" button if not on the last page
  if (pagina_actual < totalPaginas) {
    let nextButton = crearBotonDePagina(pagina_actual + 1, '»');
    container.appendChild(nextButton);
  }
}

// This function creates an individual page button
function crearBotonDePagina(numeroPagina, texto) {
  let button = document.createElement('a');
  button.innerText = texto;
  button.href = `javascript:void(0);`; // Prevent the default link behavior
  button.addEventListener('click', function(e) {
    e.preventDefault();
    cambiarPagina(numeroPagina);
  });
  return button;
}

// This function changes the page and updates the table and pagination buttons
function cambiarPagina(nuevaPagina) {
  pagina_actual = nuevaPagina;
  let currentPageData = reshapeArray(datos_totales, maxInnerArrayLength)[pagina_actual - 1];
  buildTable(currentPageData);
  actualizarBotonesDePaginacion();
}

// FUncionts here --> 


document.addEventListener('DOMContentLoaded', function () {
  var startOffset;
  var draggedTh = null;

  // Agregar listeners a los controladores de redimensionamiento
  document.querySelectorAll('.resize-handle').forEach(handle => {
      handle.addEventListener('mousedown', function (event) {
          draggedTh = event.target.parentElement; // Columna que se está redimensionando
          startOffset = draggedTh.offsetWidth - event.pageX;
          event.preventDefault(); // Evitar la selección de texto durante el arrastre
      });
  });

  // Detectar el movimiento del mouse y ajustar el tamaño de la columna
  document.addEventListener('mousemove', function (event) {
      if (draggedTh) {
          draggedTh.style.width = startOffset + event.pageX + 'px';
      }
  });

  // Terminar el redimensionamiento cuando se suelta el botón del mouse
  document.addEventListener('mouseup', function () {
      draggedTh = null; // Finalizar el arrastre
  });
});

function get_all_updated_data() {
  // This function will be used to extract all the data 



}

function set_nombre_columna_reservada(nuevo_nombre) {
  const schema_data = {"name_reserved_column": nuevo_nombre};


  const urlWithParams = new URL(`http://${ip_api}/api_set_conf`); // Make sure to include the 'http'
  urlWithParams.searchParams.append('api_key', api_key);

  fetch(urlWithParams, {
    'method': 'POST',
    'headers': {
        'Content-Type': 'application/json'
    },
    'body': JSON.stringify(schema_data)
  })
  .then(response => {
      if (!response.ok) {
          throw new Error('Network response was not ok ' + response.statusText);
      }
      // Backend response here
      return response.json();
  })
  .then(data => {
      // here i handle the response like frontend message of all right or something was worng
      let response = data;
      console.log(response);
  })
  .catch(error => { // Debería ser .catch, no .error
      console.error("An error occurred: ", error);
  });


}

function guardar_cambios() {
  
  let reserved_column_name = document.getElementById('nombre_columna_reservada').value;

  // Guardar cambios de la columna reservada
  if (reserved_column_name) {
    set_nombre_columna_reservada(reserved_column_name);
    document.getElementById("status_message").textContent = `El nombre de la columna a sido cambiado correctamente a \"${reserved_column_name}\"`;
    document.getElementById("status_message").style = "color:#0d8500"
  }

  // Guardar otros cambios

}




// Call this function to initially load the data and set up the table and pagination buttons
async function main() {
  // Assuming setupWebSocket() is properly defined and fetches the data
  setupWebSocket();
  // Once data is loaded through the WebSocket, call this function to set up the pagination buttons
  actualizarBotonesDePaginacion(); 
}


main();