document.addEventListener('DOMContentLoaded', function() {
    const form = document.querySelector('form');
    form.addEventListener('submit', function(event) {
        event.preventDefault(); // ป้องกันการส่งฟอร์มไปยัง URL ที่ระบุในการ submit
        
        // ตรวจสอบข้อมูลที่ป้อนโดยผู้ใช้
        const firstName = document.getElementById('id_first_name').value;
        const lastName = document.getElementById('id_last_name').value;
        const username = document.getElementById('id_username').value;
        const email = document.getElementById('id_email').value;
        const password1 = document.getElementById('id_password1').value;
        const password2 = document.getElementById('id_password2').value;

        // ตรวจสอบเงื่อนไขข้อมูลที่ถูกต้อง
        if (firstName === '' || lastName === '' || username === '' || email === '' || password1 === '' || password2 === '') {
            Swal.fire({
                icon: 'error',
                title: 'โปรดกรอกข้อมูลให้ครบทุกช่อง',
            });
            return;
        }

        // ตรวจสอบว่ารหัสผ่านตรงกันหรือไม่
        if (password1 !== password2) {
            Swal.fire({
                icon: 'error',
                title: 'รหัสผ่านไม่ตรงกัน',
            });
            return;
        }

        // ตรวจสอบรหัสผ่านตามเงื่อนไขที่กำหนด
        const passwordPattern = /^(?=.*[a-zA-Z])(?=.*[0-9])(?=.*[@!#$%^&*])[a-zA-Z0-9@!#$%^&*]{8,}$/;
        if (!passwordPattern.test(password1)) {
            Swal.fire({
                icon: 'error',
                title: 'รหัสผ่านต้องไม่คล้ายกับข้อมูลส่วนตัว, มีอย่างน้อย 8 ตัวอักษร, มีตัวอักษรและตัวเลข, และมีอักขระพิเศษอย่างน้อย 1 ตัว',
            });
            return;
        }

        // กรอกข้อมูลถูกต้อง สามารถส่งฟอร์มไปยัง URL ที่ระบุได้
        form.submit();
    });
});
