document.addEventListener('DOMContentLoaded', function() {
    const userTableBody = document.querySelector('#userTableBody');
    const addUserForm = document.querySelector('#addUserForm');
    const errorContainer = document.querySelector('#errorContainer');
    const successContainer = document.querySelector('#successContainer');

    // Fetch and display users
    function fetchUsers() {
        fetch('/api/fetch_users/')
            .then(response => response.json())
            .then(data => {
                userTableBody.innerHTML = '';
                data.forEach(user => {
                    userTableBody.innerHTML += `
                        <tr>
                            <td>${user.username}</td>
                            <td>${user.email}</td>
                            <td>
                                <button 
                                    class="btn btn-danger btn-sm" 
                                    onclick="deleteUser(${user.id})"
                                >
                                    Remove
                                </button>
                            </td>
                        </tr>
                    `;
                });
            })
            .catch(error => console.error('Error fetching users:', error));
    }

    // Add a new user
    addUserForm.addEventListener('submit', function(event) {
        event.preventDefault();
        const formData = new FormData(addUserForm);
        const data = {
            username: formData.get('username'),
            email: formData.get('email'),
            password1: formData.get('password1'),
            password2: formData.get('password2')
        };

        fetch('/api/create_user/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify(data)
        })
        .then(response => {
            if (!response.ok) {
                return response.json().then(errorData => {
                    displayErrors(errorData);
                });
            }
            return response.json();
        })
        .then(data => {
            const modal = document.querySelector('#addUserModal');
            const bootstrapModal = bootstrap.Modal.getInstance(modal);
            bootstrapModal.hide();
            fetchUsers();
            errorContainer.innerHTML = '';
            displaySuccess("User added successfully!");
        })
        .catch(error => console.error('Error:', error));
    });

    // Delete a user
    window.deleteUser = function(userId) {
        fetch(`/api/delete_user/${userId}/`, {
            method: 'DELETE',
            headers: {
                'X-CSRFToken': getCookie('csrftoken')
            }
        })
        .then(() => fetchUsers())
        .catch(error => console.error('Error:', error));
    };

    // Display errors
    function displayErrors(errors) {
        errorContainer.innerHTML = '';
        for (const [field, messages] of Object.entries(errors)) {
            // Check if messages is an array; if not, convert it to an array
            const messageArray = Array.isArray(messages) ? messages : [messages];
    
            messageArray.forEach(message => {
                errorContainer.innerHTML += `
                    <div class="alert alert-danger alert-dismissible fade show">
                        ${field.charAt(0).toUpperCase() + field.slice(1)}: ${message}
                        <button 
                            type="button" 
                            class="btn-close" 
                            data-bs-dismiss="alert" 
                            aria-label="Close"
                        ></button>
                    </div>
                `;
            });
        }
        $(errorContainer).removeClass('d-none');
    }

    // Display success messages
    function displaySuccess(message) {
        successContainer.innerHTML = `
            <div class="alert alert-success alert-dismissible fade show" role="alert">
                ${message}
                <button 
                    type="button" 
                    class="btn-close" 
                    data-bs-dismiss="alert" 
                    aria-label="Close"
                ></button>
            </div>
        `;
        $(successContainer).removeClass('d-none');
    }

    // Get CSRF token
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    // Initial fetch of users
    fetchUsers();
});


// document.addEventListener('DOMContentLoaded', function() {
//     const userTableBody = document.querySelector('#userTableBody');
//     const addUserForm = document.querySelector('#addUserForm');
//     const errorContainer = document.querySelector('#errorContainer');
//     const successContainer = document.querySelector('#successContainer');

//     // Fetch and display users
//     function fetchUsers() {
//         $.ajax({
//             url: '/api/fetch_users/',
//             method: 'GET',
//             success: function(data) {
//                 userTableBody.innerHTML = '';
//                 data.forEach(user => {
//                     userTableBody.innerHTML += `
//                         <tr>
//                             <td>${user.username}</td>
//                             <td>${user.email}</td>
//                             <td>
//                                 <button 
//                                     class="btn btn-danger btn-sm" 
//                                     onclick="deleteUser(${user.id})"
//                                 >
//                                     Remove
//                                 </button>
//                             </td>
//                         </tr>
//                     `;
//                 });
//             },
//             error: function(xhr, status, error) {
//                 console.error('Error fetching users:', error);
//             }
//         });
//     }

//     // Add a new user
//     $(addUserForm).on('submit', function(event) {
//         event.preventDefault();
//         const formData = new FormData(addUserForm);
//         const data = {
//             username: formData.get('username'),
//             email: formData.get('email'),
//             password1: formData.get('password1'),
//             password2: formData.get('password2')
//         };

//         $.ajax({
//             url: '/api/create_user/',
//             method: 'POST',
//             contentType: 'application/json',
//             headers: {
//                 'X-CSRFToken': getCookie('csrftoken')
//             },
//             data: JSON.stringify(data),
//             success: function(response) {
//                 const modal = document.querySelector('#addUserModal');
//                 const bootstrapModal = bootstrap.Modal.getInstance(modal);
//                 bootstrapModal.hide();
//                 fetchUsers();
//                 errorContainer.innerHTML = '';
//                 displaySuccess("User added successfully!");
//             },
//             error: function(xhr, status, error) {
//                 xhr.responseJSON.then(function(errorData) {
//                     displayErrors(errorData);
//                 });
//             }
//         });
//     });

//     // Delete a user
//     window.deleteUser = function(userId) {
//         $.ajax({
//             url: `/api/delete_user/${userId}/`,
//             method: 'DELETE',
//             headers: {
//                 'X-CSRFToken': getCookie('csrftoken')
//             },
//             success: function() {
//                 fetchUsers();
//             },
//             error: function(xhr, status, error) {
//                 console.error('Error:', error);
//             }
//         });
//     };

//     // Display errors
//     function displayErrors(errors) {
//         errorContainer.innerHTML = '';
//         for (const [field, messages] of Object.entries(errors)) {
//             const messageArray = Array.isArray(messages) ? messages : [messages];
//             messageArray.forEach(message => {
//                 errorContainer.innerHTML += `
//                     <div class="alert alert-danger">
//                         ${field.charAt(0).toUpperCase() + field.slice(1)}: ${message}
//                     </div>
//                 `;
//             });
//         }
//         $(errorContainer).removeClass('d-none');
//     }

//     // Display success messages
//     function displaySuccess(message) {
//         successContainer.innerHTML = `
//             <div class="alert alert-success alert-dismissible fade show" role="alert">
//                 ${message}
//                 <button 
//                     type="button" 
//                     class="btn-close" 
//                     data-bs-dismiss="alert" 
//                     aria-label="Close"
//                 ></button>
//             </div>
//         `;
//         $(successContainer).removeClass('d-none');
//     }

//     // Get CSRF token
//     function getCookie(name) {
//         let cookieValue = null;
//         if (document.cookie && document.cookie !== '') {
//             const cookies = document.cookie.split(';');
//             for (let i = 0; i < cookies.length; i++) {
//                 const cookie = cookies[i].trim();
//                 if (cookie.substring(0, name.length + 1) === (name + '=')) {
//                     cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
//                     break;
//                 }
//             }
//         }
//         return cookieValue;
//     }

//     // Initial fetch of users
//     fetchUsers();
// });
