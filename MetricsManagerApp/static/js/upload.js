$(document).ready(function() {
    $('#uploadForm').on('submit', function(e) {
        e.preventDefault();  // Prevent the default form submission

        var fileInput = $('#fileInput')[0];
        if (fileInput.files.length === 0) {
            $('#statusHeader').text('No file selected.').addClass('alert-danger').removeClass('d-none');
            return;
        }

        var file = fileInput.files[0];
        var maxSize = 1 * 1024 * 1024 * 1024; // 1GB in bytes

        if (file.size > maxSize) {
            $('#statusHeader').text('File size exceeds 1GB limit.').addClass('alert-danger').removeClass('d-none');
            return;
        }

        var formData = new FormData(this);

        // Show the progress container and status header
        $('#progressContainer').removeClass('d-none');
        $('#statusHeader').removeClass('d-none').text('Uploading...').removeClass('alert-success alert-danger');

        $.ajax({
            xhr: function() {
                var xhr = new XMLHttpRequest();
                xhr.upload.addEventListener('progress', function(e) {
                    if (e.lengthComputable) {
                        var percentComplete = (e.loaded / e.total) * 100;
                        $('#progressBar').css('width', percentComplete + '%')
                                         .attr('aria-valuenow', percentComplete)
                                         .text(Math.round(percentComplete) + '%');
                    }
                }, false);
                return xhr;
            },
            type: 'POST',
            url: '/api/upload/', // URL for file upload endpoint
            data: formData,
            processData: false,
            contentType: false,
            success: function(response) {
                $('#statusHeader').text('File uploaded successfully!').addClass('alert-success').removeClass('alert-danger');
                $('#progressBar').css('width', '0%').attr('aria-valuenow', '0').text('0%'); // Reset progress bar
                setTimeout(function() {
                    $('#statusHeader').addClass('d-none');
                    $('#progressContainer').addClass('d-none');
                }, 3000); // Hide status header after 3 seconds
            },
            error: function(xhr, status, error) {
                $('#statusHeader').text('Error uploading file: ' + xhr.responseJSON.error).addClass('alert-danger').removeClass('alert-success');
                $('#progressBar').css('width', '0%').attr('aria-valuenow', '0').text('0%'); // Reset progress bar
                setTimeout(function() {
                    $('#statusHeader').addClass('d-none');
                    $('#progressContainer').addClass('d-none');
                }, 3000); // Hide status header after 3 seconds
            }
        });
    });
});
