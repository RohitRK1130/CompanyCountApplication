$(document).ready(function() {
    // Initial population of dropdowns
    populateDropdowns();

    // Function to populate dropdowns
    function populateDropdowns() {
        $.ajax({
            url: '/api/query-builder-data/',
            type: 'GET',
            success: function(response) {
                populateDropdown('industry', response.industries);
                populateDropdown('year', response.years);
                populateDropdown('country', response.countries);
                // Clear dependent dropdowns
                $('#state').empty().append('<option value="">Select State</option>');
                $('#city').empty().append('<option value="">Select City</option>');
            },
            error: function() {
                alert('Error fetching dropdown data.');
            }
        });
    }

    // Function to populate a dropdown element
    function populateDropdown(id, options) {
        var dropdown = $('#' + id);
        dropdown.empty(); // Clear existing options
        dropdown.append($('<option></option>').val('').html('Select ' + id.charAt(0).toUpperCase() + id.slice(1))); // Add default option
        $.each(options, function(index, value) {
            dropdown.append($('<option></option>').val(value).html(value));
        });
    }

    // Function to update dependent dropdowns

    function updateCountryDropdowns() {
        const country = $('#country').val();

        if (country) {
            $.ajax({
                url: '/api/get-states/',
                type: 'GET',
                data: { country: country },
                success: function(response) {
                    populateDropdown('state', response.states);
                },
                error: function() {
                    alert('Error fetching states.');
                }
            });
        } else {
            $('#state').empty().append('<option value="">Select State</option>');
            $('#city').empty().append('<option value="">Select City</option>');
        }
    };

    function updateStateDropdowns() {

        const state = $('#state').val();
        // Only update cities if a state is selected
        if (state) {
            $.ajax({
                url: '/api/get-cities/',
                type: 'GET',
                data: { state: state },
                success: function(response) {
                    populateDropdown('city', response.cities);
                },
                error: function() {
                    alert('Error fetching cities.');
                }
            });
        } else {
            $('#city').empty().append('<option value="">Select City</option>');
        }
    }

    // Event listeners for dropdown changes
    $('#country').on('change', function() {
        updateCountryDropdowns();
    });

    $('#state').on('change', function() {
        updateStateDropdowns();
    });

    // Handle the form reset
    $('#queryForm').on('reset', function() {
        // Optional: Clear any result alerts or other dynamic elements
        $('#resultAlert').empty();
        console.log('Form has been reset');
    });

    // Function to display success message
    function displaySuccess(count) {
        $('#resultAlert').html(`
            <div class="alert alert-success alert-dismissible fade show" role="alert">
                Record Count: <span id="count">${count}</span>
                <button 
                    type="button" 
                    class="btn-close" 
                    data-bs-dismiss="alert" 
                    aria-label="Close"
                ></button>
            </div>
        `);
    }

    // Handle form submission
    $('#queryForm').on('submit', function(e) {
        e.preventDefault();

        var queryParams = {
            keyword: $('#keyword').val(),
            industry: $('#industry').val(),
            year: $('#year').val(),
            city: $('#city').val(),
            state: $('#state').val(),
            country: $('#country').val(),
            employee_from: $('#employee_from').val(),
            employee_to: $('#employee_to').val()
        };

        $.ajax({
            url: '/api/query/',
            type: 'GET',
            data: queryParams,
            success: function(response) {
                if (response.count !== undefined) {
                    displaySuccess(response.count);
                } else {
                    alert('No count returned from the server.');
                }
            },
            error: function() {
                alert('Error querying data.');
            }
        });
    });
});
