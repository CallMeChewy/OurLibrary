
const nodemailer = require('nodemailer');

async function testSmtp() {
    try {
        const transporter = nodemailer.createTransport({
            host: 'smtp.misk.com',
            port: 587,
            connectionTimeout: 30000,
            auth: {
                user: 'Herb@BowersWorld.com',
                pass: 'IChewy#4'
            }
        });

        const mailOptions = {
            from: 'ProjectHimalaya@BowersWorld.com',
            to: 'test@example.com',
            subject: 'Test Email from Nodemailer',
            text: 'This is a test email sent from a Node.js script using Nodemailer.'
        };

        const info = await transporter.sendMail(mailOptions);
        console.log('Email sent: ' + info.response);
    } catch (error) {
        console.error('Error sending email:', error);
    }
}

testSmtp();
