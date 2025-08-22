const {onCall} = require("firebase-functions/v2/https");
const {setGlobalOptions} = require("firebase-functions/v2");
const nodemailer = require("nodemailer");
const admin = require("firebase-admin");

admin.initializeApp();

// Limit concurrency
setGlobalOptions({maxInstances: 10});

/**
 * Send a verification email using Misk SMTP
 */
exports.sendVerificationEmail = onCall(
    async (request) => {
      console.log("sendVerificationEmail function invoked");
      const data = request.data;
      console.log("Function called with data:", data);
      console.log("Request:", request);

      const {email} = data;
      console.log("Extracted email:", email);
      if (!email) {
        console.error("No email provided in data:", data);
        throw new Error("Email is required.");
      }

      console.log("Creating Misk.com SMTP transporter...");
      const transporter = nodemailer.createTransport({
        host: "smtp.misk.com",
        port: 587,
        secure: false, // Use STARTTLS for port 587
        debug: true,
        logger: true,
        auth: {
          user: "Herb@BowersWorld.com",
          pass: "IChewy#4",
        },
      });

      console.log("Sending verification email...");
      // Use the verification code passed from the web interface
      const verificationCode = data.code || Math.random().toString(36)
          .substring(2, 8).toUpperCase();

      const emailHtml = `
        <div style="font-family: Arial, sans-serif; max-width: 600px;">
          <h2 style="color: #2563eb;">Email Verification Required</h2>
          <p>Hello,</p>
          <p>Please verify your email address for your OurLibrary account.</p>
          <div style="background: #f3f4f6; padding: 20px; margin: 20px 0; 
                      text-align: center; border-radius: 8px;">
            <strong style="font-size: 18px; color: #1f2937;">
              ${verificationCode}
            </strong>
          </div>
          <p>Enter this code on the verification page to complete your 
             account setup.</p>
          <p>This code expires in 24 hours.</p>
          <hr style="margin: 30px 0;">
          <p style="color: #6b7280; font-size: 12px;">
            OurLibrary Educational Platform<br>
            If you didn't request this, please ignore this email.
          </p>
        </div>
      `;

      await transporter.sendMail({
        from: `"OurLibrary" <ProjectHimalaya@BowersWorld.com>`,
        to: email,
        subject: "Email Verification Code",
        text: `Your OurLibrary verification code is: ${verificationCode}`,
        html: emailHtml,
      });

      console.log("Email sent successfully to:", email);

      return {success: true, message: "Verification email sent."};
    },
);

/**
 * Send a password reset email using Misk SMTP
 */
exports.sendPasswordResetEmail = onCall(
    async (request) => {
      const data = request.data;
      console.log("Password reset function called with data:", data);
      console.log("Request:", request);

      const {email} = data;
      console.log("Extracted email:", email);
      if (!email) {
        console.error("No email provided in data:", data);
        throw new Error("Email is required.");
      }

      console.log("Creating Misk.com SMTP transporter...");
      const transporter = nodemailer.createTransport({
        host: "smtp.misk.com",
        port: 587,
        secure: false, // Use STARTTLS for port 587
        debug: true,
        logger: true,
        auth: {
          user: "Herb@BowersWorld.com",
          pass: "IChewy#4",
        },
      });

      console.log("Sending password reset email...");
      const resetToken = Math.random().toString(36)
          .substring(2, 12).toUpperCase();

      const emailHtml = `
        <h2>Password Reset Request</h2>
        <p>You requested a password reset for your OurLibrary account.</p>
        <p>Your reset token is: <strong>${resetToken}</strong></p>
        <p>Please use this token to reset your password.</p>
        <p>This token will expire in 1 hour.</p>
        <br>
        <p>If you didn't request this reset, please ignore this email.</p>
        <p>Best regards,<br>The OurLibrary Team</p>
      `;

      await transporter.sendMail({
        from: `"OurLibrary" <ProjectHimalaya@BowersWorld.com>`,
        to: email,
        subject: "OurLibrary - Password reset request",
        text: `Your password reset token is: ${resetToken}`,
        html: emailHtml,
      });

      console.log("Password reset email sent successfully to:", email);

      return {success: true, message: "Password reset email sent."};
    },
);
