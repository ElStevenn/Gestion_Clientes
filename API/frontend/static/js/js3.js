console.log("Hello world!");
let apikey = 'rmpxCixzGRet81UnltZUBLdURHhnJy4QSltELa6HjU8=';
let ip = "185.254.206.129"; // Pau, you will need to change this

async function createSession(username, password) {
    try {
        
        let body_request = {
            "username":username,
            "password": password
        }

        const response = await fetch(`http://${ip}/create_session`, {
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
        console.error("An error occurred with CreateSession: ", error);
    }
}



document.addEventListener('DOMContentLoaded', function() {
    document.getElementById('button_login_submit').addEventListener('click',async function(event) {
        event.preventDefault();

        let username = document.getElementById('username').value;
        let password = document.getElementById('password').value;

        const session = await createSession(username, password);
;
        if (session.status == "failed") {
            // Handle error, in   this case notify the client that his password is worng
            document.getElementById('status_message').textContent = session.response;
            document.getElementById('status_message').style = "color: #ad0014;"

        } else{
            // Create cookie and store id in his navegator
            console.log("*redirecting to /apiconf and creating a new session cookie.In theory the createSessionhas to be that*")
            

        }


    });
});
