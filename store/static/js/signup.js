
function handleFormSubmit(event) {
    event.preventDefault(); 
    
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
            title: 'รหัสผ่านไม่ถูกต้อง',
            text: '• รหัสผ่านของคุณต้องไม่คล้ายกับข้อมูลส่วนตัวอื่น ๆ ของคุณ\n• รหัสผ่านของคุณต้องมีอย่างน้อย 8 ตัวอักษร\n• รหัสผ่านของคุณต้องไม่ใช่รหัสผ่านที่ใช้กันอย่างแพร่หลาย\n• รหัสผ่านของคุณต้องไม่มีแต่ตัวเลขเท่านั้น\n• รหัสผ่านต้องมีอักขระพิเศษ (@, +, -, _) อย่างน้อย 1 ตัว',
        });
        return;
    }

    // กรอกข้อมูลถูกต้อง สามารถส่งฟอร์มไปยัง URL ที่ระบุได้
    Swal.fire({
        position: "top-end",
        icon: "success",
        title: "Your work has been saved",
        showConfirmButton: false,
        timer: 1500
      });
    event.target.submit();
}

document.addEventListener('DOMContentLoaded', function() {
    const form = document.querySelector('form');
    form.addEventListener('submit', handleFormSubmit);
});
