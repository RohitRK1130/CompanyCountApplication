$(document).ready(function() {
    const userTableBody = $('#userTableBody');
    const addUserForm = $('#addUserForm');
    const errorContainer = $('#errorContainer');
    const successContainer = $('#successContainer');

    // Fetch and display users
    function fetchUsers() {
        $.ajax({
            url: '/api/fetch_users/',
            method: 'GET',
            success: function(data) {
                userTableBody.empty();
                data.forEach(user => {
                    userTableBody.append(`
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
                    `);
                });
            },
            error: function(xhr, status, error) {
                console.error('Error fetching users:', error);
            }
        });
    }

    // Add a new user
    addUserForm.on('submit', function(event) {
        event.preventDefault();
        const formData = new FormData(this);
        const data = {
            username: formData.get('username'),
            email: formData.get('email'),
            password1: formData.get('password1'),
            password2: formData.get('password2')
        };

        $.ajax({
            url: '/api/create_user/',
            method: 'POST',
            contentType: 'application/json',
            headers: {
                'X-CSRFToken': getCookie('csrftoken')
            },
            data: JSON.stringify(data),
            success: function() {
                const modal = $('#addUserModal');
                const bootstrapModal = bootstrap.Modal.getInstance(modal[0]);
                bootstrapModal.hide();
                fetchUsers();
                errorContainer.empty();
                displaySuccess("User added successfully!");
            },
            error: function(xhr, status, error) {
                displayErrors(xhr.responseJSON);
            }
        });
    });

    // Delete a user
    window.deleteUser = function(userId) {
        $.ajax({
            url: `/api/delete_user/${userId}/`,
            method: 'DELETE',
            headers: {
                'X-CSRFToken': getCookie('csrftoken')
            },
            success: function() {
                fetchUsers();
            },
            error: function(xhr, status, error) {
                console.error('Error:', error);
            }
        });
    };

    // Display errors
    function displayErrors(errors) {
        errorContainer.empty();
        $.each(errors, function(field, messages) {
            const messageArray = Array.isArray(messages) ? messages : [messages];
            messageArray.forEach(message => {
                errorContainer.append(`
                    <div class="alert alert-danger alert-dismissible fade show">
                        ${field.charAt(0).toUpperCase() + field.slice(1)}: ${message}
                        <button 
                            type="button" 
                            class="btn-close" 
                            data-bs-dismiss="alert" 
                            aria-label="Close"
                        ></button>
                    </div>
                `);
            });
        });
        errorContainer.removeClass('d-none');
    }

    // Display success messages
    function displaySuccess(message) {
        successContainer.html(`
            <div class="alert alert-success alert-dismissible fade show" role="alert">
                ${message}
                <button 
                    type="button" 
                    class="btn-close" 
                    data-bs-dismiss="alert" 
                    aria-label="Close"
                ></button>
            </div>
        `);
        successContainer.removeClass('d-none');
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
