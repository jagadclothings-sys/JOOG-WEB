@echo off
echo ========================================
echo    JOOG Influencer System Launcher
echo ========================================
echo.
echo Opening Influencer System in your browser...
echo.
echo Available URLs:
echo 1. Direct Access Page (with credentials)
echo 2. System Info Page  
echo 3. Login Page
echo.

start http://127.0.0.1:8000/influencers/access/

echo ✅ Browser opened!
echo.
echo 🔑 Quick Credentials:
echo Username: johndoe
echo API Key: mXBsC...1hedV (full key in access page)
echo.
echo 📋 What to do next:
echo 1. Click "Auto Login as johndoe" button
echo 2. Or go to login page and enter credentials manually
echo 3. Explore dashboard, orders, and profile
echo.
echo Press any key to close...
pause > nul