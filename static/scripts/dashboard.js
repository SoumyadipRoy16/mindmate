        function previewImage(input) {
            const file = input.files[0];
            const reader = new FileReader();
            reader.onload = function (e) {
                document.getElementById('avatar-img').src = e.target.result;
            };
            reader.readAsDataURL(file);
        }