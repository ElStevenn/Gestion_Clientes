console.log("Hello world!");
let apikey = 'rmpxCixzGRet81UnltZUBLdURHhnJy4QSltELa6HjU8=';
let ip = "185.254.206.129"; // Pau, you will need to change this

async function login(username, password) {
    try {
        
        let body_request = {
            "username":username,
            "password": password
        }

        const response = await fetch(`http://${ip}/login`, {
            method: 'POST',
            headers: {
                "Content-Type": "application/json",
                // Add apikey here if is required
            },
            body: JSON.stringify(body_request)
        });

        if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
        }

        const result = await response.json();
        console.log("Success", result);

        return result;

    } catch (error) {
        console.error("An error occurred with checkUsername: ", error);
    }
}

async function setSession(sessionData){
    const response = await fetch(`http://${ip}/set-session`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(sessionData),
    credentials: 'include'
  });
  const responseData = await response.json();
  // Set session into like it was a cookie
  document.cookie = `session_id = ${responseData.session_id}`

  return responseData
}







/*
async function login(username,password) {
    try{
        const body_request = {"username":username, "password":password} 
        const response = await fetch(`http://${ip}/login?response=response`, {
            method: 'POST',
            headers: {
                "Content-Type": "application/json",
                // Add apikey here if is required
            },
            body: JSON.stringify(body_request),
            credentials: 'include' // This is necesary to include cookies
        });

        if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
        }

        const result = await response.json();
        return result;


    } catch(error) {
        console.log("An error ocrred with createSession:", error);
        return null;
    }
}
*/
async function whoAmi() {
    try{

        let session_id_boddy = {'sessionStorage':document.cookie}
        console.log(session_id_boddy);
        
        const response = await fetch(`http://${ip}/get-session`, {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
        body: JSON.stringify(session_id_boddy),
        credentials: 'include'})
        
        return response.json();

    } catch(error) {
        console.error("An error ocurred with whoAmi: ", error)
    }
}

document.addEventListener('DOMContentLoaded', async function() {
    document.getElementById('button_login_submit').addEventListener('click', async function(event) {
        event.preventDefault();
    
        let username = document.getElementById('username').value;
        let password = document.getElementById('password').value;
        const request = await login(username, password);
    
        // Check if the login request was unsuccessful
        if (!request || request.status === "failed") {
            // Handle error, notify the client that there's an issue (e.g., wrong password or network error)
            const errorMessage = request ? request.response : "Login failed due to a network error.";
            document.getElementById('status_message').textContent = errorMessage;
            document.getElementById('status_message').style = "color: #ad0014;";
        } else {
            // Proceed with session creation
            document.getElementById('status_message').textContent = "";
            const session_data = { "username": username };
            let session_ = await setSession(session_data);
            console.log(session_);
        }
    });
    
});


async function main(){
    const whoami_ = await whoAmi();
    console.log(whoami_);

}
main();