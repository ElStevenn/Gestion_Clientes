console.log("Hello world!");
let apikey = 'rmpxCixzGRet81UnltZUBLdURHhnJy4QSltELa6HjU8=';
let ip = "185.254.206.129";


async function login(username, password) {
    try {
        const body_request = new URLSearchParams();
        body_request.append("username", username);
        body_request.append("password", password);
        
        const response = await fetch("http://inutil.top/token", {
            method: "POST",
            headers: {
                "Content-Type": "application/x-www-form-urlencoded",
                "api-key": apikey // Ensure apikey is defined and valid
            },
            body: body_request
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
        }

        const result = await response.json();
        console.log("Success", result);

        return result;

    } catch (error) {
        console.error("An error occurred with login: ", error);
    }
}


function getCookieByName(cookieName) {
    const cookies = document.cookie.split('; ');
  
    for (const cookie of cookies) {
      const [name, value] = cookie.split('=');
      if (name === cookieName) {
        return value;
      }
    }
  
    // If the cookie with the specified name is not found, return null or an empty string as desired.
    return null;
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
    // Verify if the user is already logged
    try{
        const token_beaber = getCookieByName('token_beaber')
        if (!token_beaber){
            // Verify if the user doesn't have session token
            console.log("The user doesn't have any token asociated")
        }else{
            // Send a login to autenticate the user, credentials and check if tht user has the correct credentials
            let request_body = {'token_beaber':token_beaber}
            console.log(request_body);
            
            const response = await fetch(`http://inutil.top/login`, {
                method: 'POST',
                headers: {
                  'Content-Type': 'application/json',
                  'api-key': apikey
                },
            body: JSON.stringify(request_body),
            credentials: 'include'})
            
            return response.json();
        }
    } catch(error) {
        console.error("An error ocurred with whoAmi: ", error)
    }
}

document.addEventListener('DOMContentLoaded', async function() {
    document.getElementById('button_login_submit').addEventListener('click', async function(event) {
        event.preventDefault();
    
        let username = document.getElementById('username').value;
        let password = document.getElementById('password').value;
        try{
            const request = await login(username, password);
            console.log(request);

        }catch(e){
            // Handle error, notify the client that there's an issue (e.g., wrong password or network error)
            const errorMessage = request ? request.response : "Login failed due to a network error.";
            document.getElementById('status_message').textContent = errorMessage;
            document.getElementById('status_message').style = "color: #ad0014;";
        }
        
    
      
    });
    
});


async function main(){
    const whoami_ = await whoAmi();
    console.log("whoami response (delete this): ",whoami_);

}
main();

