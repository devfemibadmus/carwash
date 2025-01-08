var api_endpoint = "https://us-central1-dev-femi-badmus.cloudfunctions.net/carwash"

// API fetch car types and load
function loadCartype() {
    fetch(api_endpoint + '/cartype')
        .then(response => response.json())
        .then(data => {
            const vehicleSelect = document.querySelectorAll('.form-select')[0];
            const pricingSelect = document.querySelectorAll('.form-select')[1];

            data.forEach(car => {
                const option = document.createElement('option');
                option.value = car.name;
                option.textContent = car.name;
                vehicleSelect.appendChild(option);
            });

            vehicleSelect.addEventListener('change', function () {
                const selectedVehicle = vehicleSelect.value;
                pricingSelect.innerHTML = '<option selected="">Select Pricing Plan</option>';

                data.forEach(car => {
                    if (car.name === selectedVehicle) {
                        const premiumOption = document.createElement('option');
                        premiumOption.value = 'premium';
                        premiumOption.textContent = `Premium: $${car.premium}`;
                        pricingSelect.appendChild(premiumOption);

                        const standardOption = document.createElement('option');
                        standardOption.value = 'standard';
                        standardOption.textContent = `Standard: $${car.standard}`;
                        pricingSelect.appendChild(standardOption);
                    }
                });
            });
        })
        .catch(error => console.error('Error fetching data:', error));
}

// Google map
async function init() {
    await customElements.whenDefined('gmp-map');

    const map = document.querySelector('gmp-map');
    const marker = document.querySelector('gmp-advanced-marker');
    const placePicker = document.querySelector('gmpx-place-picker');
    const infowindow = new google.maps.InfoWindow();
    if (!map.innerMap) {
        console.log('Map is not initialized yet');
        return;
    }

    map.innerMap.setOptions({
        mapTypeControl: false
    });
    map.addEventListener('click', (event) => {
        const location = event.latLng;
        marker.position = location;
        map.center = location;
        map.zoom = 17;

        // Reverse geocoding to get the address
        const geocoder = new google.maps.Geocoder();
        geocoder.geocode({
            location: location
        }, (results, status) => {
            if (status === 'OK' && results[0]) {
                const address = results[0].formatted_address;
                infowindow.setContent(
                    `<strong>${results[0].formatted_address}</strong>`
                );
                infowindow.open(map.innerMap, marker);
                document.getElementById('address').value = address;
            }
        });
    });

    placePicker.addEventListener('gmpx-placechange', () => {
        const place = placePicker.value;

        if (!place.location) {
            window.alert("No details available for input: '" + place.name + "'");
            infowindow.close();
            marker.position = null;
            return;
        }

        marker.position = place.location;
        map.center = place.location;
        map.zoom = 17;

        infowindow.setContent(
            `<strong>${place.displayName}</strong><br>
         <span>${place.formattedAddress}</span>`
        );
        infowindow.open(map.innerMap, marker);
        document.getElementById('address').value = place.formattedAddress;
    });
}

// Checkout payment
function payNowBtn() {
    $('#errorModal').modal('hide');
    const loadingModalElement = document.getElementById('loadingModal');
    const errorModalElement = document.getElementById('errorModal');
    const loadingModal = new bootstrap.Modal(loadingModalElement);
    const errorModal = new bootstrap.Modal(errorModalElement);

    loadingModal.show();

    const data = {
        address: document.getElementById('address').value,
        car_type_name: document.getElementById('vehicleType').value,
        wash_type: document.getElementById('pricingPlan').value,
        status: "pending",
        quantity: parseInt(document.getElementById('quality').value, 10),
        payment_id: "payment_789",
        redirect_url: window.location.origin
    };
    grecaptcha.enterprise.ready(async () => {
        try {
            const token = await grecaptcha.enterprise.execute('6LcqVbEqAAAAAH1KgZju7V7Vzexy9e2zSm69MMh4', {
                action: 'ORDER'
            });
            data.recaptcha_token = token;
            const response = await fetch(api_endpoint + '/order', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(data)
            });
            const result = await response.json();
            loadingModal.hide();
            if (result.payment_url) {
                window.location.href = result.payment_url;
            } else {
                errorModalElement.querySelector('.modal-body').textContent = result.error || "Payment URL not available.";
                errorModal.show();
            }
        } catch (error) {
            loadingModal.hide();
            console.error('Error:', error);
            errorModalElement.querySelector('.modal-body').textContent = "An error occurred. Please try again.";
            errorModal.show();
        }
    });
}

// Verify payment
function verifyPayment() {
    const urlParams = new URLSearchParams(window.location.search);
    const sessionId = urlParams.get('session_id');

    if (sessionId) {
        fetch(`${api_endpoint}/payment/verify?session_id=${sessionId}`)
            .then(response => response.json())
            .then(responseData => {
                const modalBody = document.querySelector('#errorModal .modal-body');
                modalBody.textContent = responseData.message;
                const errorModal = new bootstrap.Modal(document.getElementById('errorModal'));
                errorModal.show();
            })
            .catch(error => {
                console.error('Error:', error);
            });

        document.getElementById('errorModal').addEventListener('hidden.bs.modal', function () {
            urlParams.delete('session_id');
            window.history.replaceState(null, '', window.location.pathname);
        });
    }
};


document.querySelector('form').addEventListener('submit', function (event) {
    event.preventDefault();

    let isValid = true;
    let errors = [];

    const vehicleType = document.getElementById('vehicleType').value;
    const pricingPlan = document.getElementById('pricingPlan').value;
    const name = document.querySelector('input[name="name"]').value.trim();
    const phone = document.getElementById('phone').value;
    const address = document.getElementById('address').value.trim();
    const quality = document.getElementById('quality').value;

    if (vehicleType === "" || vehicleType === "Select Vehicle Type") {
        isValid = false;
        errors.push("Vehicle Type");
    }

    if (pricingPlan === "" || pricingPlan === "Select Pricing Plan") {
        isValid = false;
        errors.push("Pricing Plan");
    }

    if (name === "") {
        isValid = false;
        errors.push("Name");
    }

    if (phone.length > 15) {
        isValid = false;
        errors.push("Phone Number");
    }

    if (address === "") {
        isValid = false;
        errors.push("Address");
    }

    if (quality === "" || isNaN(quality) || parseInt(quality) <= 0) {
        isValid = false;
        errors.push("Quality");
    }

    const modalBody = document.querySelector('#errorModal .modal-body');

    if (isValid) {
        modalBody.innerHTML = `<p>All fields are valid. What would you like to do?</p>
                               <button class="btn btn-primary" id="payNowBtn" onclick="payNowBtn()">Pay Now</button>
                               <button class="btn btn-secondary" id="sendMailBtn" onclick="sendMailBtn()">Send to Mail</button>`;
        $('#errorModal').modal('show');
    } else {
        modalBody.innerHTML = `<p>Please fill in the following fields correctly: ${errors.join(', ')}</p>`;
        $('#errorModal').modal('show');
    }

});

function sendMailBtn() {
    modalBody.innerHTML = `<input type="email" id="userEmail" class="form-control" placeholder="Enter your email" required> <button class="btn btn-primary mt-2" id="submitEmailBtn" onclick="submitEmailBtn()">Submit</button>`;
};

function submitEmailBtn() {
    const email = document.getElementById('userEmail').value;
    if (email) {
        modalBody.innerHTML = `<p>Email sent successfully to ${email}!</p>`;
        $('#errorModal').modal('show');
        setTimeout(function () {
            location.reload();
        }, 2000);
    } else {
        modalBody.innerHTML = `<p>Please enter a valid email address.</p>`;
        $('#errorModal').modal('show');
    }
};

loadCartype();
verifyPayment();
document.addEventListener('DOMContentLoaded', init);
document.getElementById('start').value = new Date().toISOString().split('T')[0];