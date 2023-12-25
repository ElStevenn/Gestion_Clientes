console.log("Hello world! this is working!");
let ip_api = "185.254.206.129"; // Change this in case that we want to change of server, but there is a way to do not use this
let apikey = document.getElementById('apikey').value;


function get_all_data_from_html(){
    // This function is used to extract all the inputs value from the HTML

    // Default
    let apikey = document.getElementById('apikey').value;
    let host = document.getElementById('host').value;
    let port = document.getElementById('port').value;

    // Email
    let email_sender = document.getElementById('email_sender').value;
    let app_password = document.getElementById('app_password').value;
    let email_reciver = document.getElementById('email_reciver').value;

    // Otros
    let max_columns_frontend = document.getElementById('max_columnas_frontend').value;
    let name_reserved_column = document.getElementById('nombre_columna_reservada').value;

    // Oauth2
    let username = document.getElementById('username').value;
    let password = document.getElementById('password').value;

    let spreadsheetID = document.getElementById('spreadsheetID').value;

    // Handle possible issues
    if (password.length < 9) {
        return {"status":"error","result": {"message":"La contraseña es demasiado corta!"}};
    } else if (apikey.includes(" ")) {
        return {"status":"error", "result": {"message": "La apikey no puede tener espacios en el medio."}};
    } else if (!email_sender.includes("@")) {
        return {"status":"error", "result": {"message": "El email sender no está en un formato correcto."}};
    } else if (!email_reciver.includes("@")) {
        return {"status":"error", "result": {"message": "El email reciver no está en un formato correcto."}};
    } else if(isNaN(Number(port))) { 
        return {"status":"error", "result": {"message": "El email reciver no está en un formato correcto."}};
    } else if (isNaN(Number(max_columns_frontend))) {
        return {"status":"error", "result": {"message": "El campo 'Máximo numero de filas' debe de ser un numero entero"}};
    }
 
    return {
        "status":"sucsess", "result":{
            "apikey":apikey, "host":host, "port":port, "email_sender":email_sender,
            "app_password": app_password, "email_reciver": email_reciver, "max_columns_frontend":max_columns_frontend,
            "name_reserved_column": name_reserved_column, "username": username, "password": password, "spreadsheetID": spreadsheetID
        }
    };
}

/*
window.onload = function() {
    window.open('/mi_pagina', 'Mi Página', 'width=600,height=400');
    window.close();
};
*/

// Event listener for the form submission
document.addEventListener('DOMContentLoaded', function() {
    document.getElementById('buttonSubmit').addEventListener('click', function(event) {
        event.preventDefault();
        
        let page_status = get_all_data_from_html();
        
        if  (page_status.status == "error") {
            document.getElementById("status_message").textContent = page_status.result.message;
            document.getElementById("status_message").style = "color:red";

        } else {
            document.getElementById("status_message").textContent = "La configuración se ha actualizado correctamente!";
            document.getElementById("status_message").style = "color:#0d8500";

            let new_data_updated = page_status.result;
            // Request body
            const schema_data = {
                "apikey": new_data_updated.apikey,
                "host": new_data_updated.host,
                "port": new_data_updated.port,
                "email_sender": new_data_updated.email_sender,
                "app_password": new_data_updated.app_password,
                "email_reciver": new_data_updated.email_reciver,
                "max_columns_frontend": new_data_updated.max_columns_frontend,
                "name_reserved_column": new_data_updated.name_reserved_column,
                "username": new_data_updated.username,
                "password": new_data_updated.password,
                "spreadsheetID":new_data_updated.spreadsheetID
              }

            // Url with apikey param
            const urlWithParams = new URL(`http://${ip_api}/api_set_conf`); // Make sure to include the http
            urlWithParams.searchParams.append('api_key', apikey);

            // Send here the data to frontend
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
                // Respuesta del backend aquí
                return response.json();
            })
            .then(data => {
                // here i handle the response
                let response = data;
                console.log(response);
            })
            .catch(error => { // Debería ser .catch, no .error
                console.error("An error occurred: ", error);
            });

            // Print response, then will be used to handle the frontend
            

        }

    });
});

/*
async function whoAmi() {
    try{
        // Change this so that i can identidy whoami
        const response = await fetch('/get-session');
        const data = await response.json();
            
        return data;

    } catch(error) {
        console.error("An error ocurred with whoAmi: ", error)
    }
}

async function deleteSession() {
    try {
        const response = await fetch("/delete_session", {
            method: 'POST',
            credentials: 'include'
        });
        const data = await response.json();
        console.log(data.response);

        return data.response;

    } catch(error) {
        console.log("An error ocurred with delete session: ", error)
    }
}
    

async function manageSessions() {
    try{

        // Check if there is an active session
        const sessionData = await whoAmi();

        // if there is a session data,  update the UI accordingly
        if (sessionData && sessionData.username) {
            console.log(`User loged in ${sessionData.username}`)

            

        } else{
            // Redirect to login page
            window.location.href = '/api_conf_login';
        }

    }catch(error) {
        console.error("An error ocurred with manageSessions:", error)

        // In case of error (e.g., unable to verify session), also redirect to login
        window.location.href = '/api_conf_login';
    }
}

manageSessions();
*/
// This part will be used to login Part, thefore do not delete please
/*
document.getElementById('loginForm').addEventListener('submit', function(event) {
    event.preventDefault();

    var username = this.username.value;
    var password = this.password.value;

    // Conect with backend oauth2
    fetch('/token', {
        "method": "POST",
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded'
        },
        body: `username=${encodeURIComponent(username)}&password=${encodeURIComponent(password)}`

    })
    .then(response => response.json())
    .then(data => {
        if (data.acces_token) {
            // Store the token in local storage or cookies
            localStorage.setItem('access_token', data.access_token);

            // Redirect to the protected endpoint or refresh the current page
            window.location.href = '/apiconf';
        } else {
            // Handle error, such as displaying a message to the user
            alert("El login ha ido mal!");
        }
    })
    .catch(error => console.error('Error:', error));


});
*/





