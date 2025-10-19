# 🚀 JOOG Influencer System - Complete User Guide

## 📍 **WHERE TO ACCESS THE SYSTEM**

### **For Influencers - LOGIN URLs:**

1. **Main Influencer System Page:**
   ```
   http://127.0.0.1:8000/influencers/
   ```
   - Shows system information and login options
   - Has direct links to login page

2. **Direct Login Page:**
   ```
   http://127.0.0.1:8000/influencers/login/
   ```
   - Manual login with username and API key

3. **Test Login Link (for johndoe):**
   ```
   http://127.0.0.1:8000/influencers/login/?username=johndoe&api_key=mXBsCGJHqsFo7ChNFffFihOrhjtGgPmpadp2bMZ81TSkD2KyAVj1hedVcw3hkNaR
   ```
   - Direct access to dashboard (auto-login)

---

## 🔐 **HOW INFLUENCERS ARE CREATED (REGISTRATION)**

**❗ IMPORTANT:** Influencers **CANNOT register themselves**. Only administrators can create influencer accounts.

### **Admin Creates Influencers Using:**

#### **Method 1: Management Command (Recommended)**
```bash
python manage.py create_influencer "Influencer Name" "email@example.com" "username" --commission 5.0
```

**Example:**
```bash
python manage.py create_influencer "Sarah Fashion" "sarah@fashion.com" "sarahfashion" \
    --phone "+1234567890" \
    --instagram "sarah_fashion_guru" \
    --youtube "SarahFashionTV" \
    --commission 7.5
```

#### **Method 2: Django Admin Panel**
```
http://127.0.0.1:8000/admin/
```
- Login as admin
- Go to "Influencers" section
- Create new influencer manually

---

## 👤 **CURRENT TEST ACCOUNTS**

### **Test Influencer #1: johndoe**
- **Username:** `johndoe`
- **Name:** John Doe
- **Email:** john.doe@example.com
- **API Key:** `mXBsCGJHqsFo7ChNFffFihOrhjtGgPmpadp2bMZ81TSkD2KyAVj1hedVcw3hkNaR`
- **Commission Rate:** 7.5%
- **Instagram:** @johndoe_fashion
- **Assigned Coupon:** JOHNDOE20 (20% off)

**Direct Access Link:**
```
http://127.0.0.1:8000/influencers/login/?username=johndoe&api_key=mXBsCGJHqsFo7ChNFffFihOrhjtGgPmpadp2bMZ81TSkD2KyAVj1hedVcw3hkNaR
```

---

## 🎯 **HOW TO TEST THE SYSTEM**

### **Step 1: Access the Main Page**
Visit: `http://127.0.0.1:8000/influencers/`
- Shows system overview
- Links to login page
- Admin instructions

### **Step 2: Login as Test Influencer**
**Option A: Use Direct Link**
- Click the "Test Login Link" on the main page
- Or use the direct access link above

**Option B: Manual Login**
- Go to: `http://127.0.0.1:8000/influencers/login/`
- Enter:
  - Username: `johndoe`
  - API Key: `mXBsCGJHqsFo7ChNFffFihOrhjtGgPmpadp2bMZ81TSkD2KyAVj1hedVcw3hkNaR`

### **Step 3: Explore Dashboard Features**
Once logged in, you can access:

1. **Dashboard:** `http://127.0.0.1:8000/influencers/dashboard/`
   - View performance statistics
   - See recent orders
   - Track commission earnings
   - Monitor coupon usage

2. **Orders:** `http://127.0.0.1:8000/influencers/orders/`
   - View all orders using your coupons
   - Filter by status or coupon code
   - See customer details and amounts

3. **Profile:** `http://127.0.0.1:8000/influencers/profile/`
   - View personal information
   - See assigned coupon codes
   - Check social media links
   - View API key details

---

## 🛠 **FOR ADMINISTRATORS**

### **Creating New Influencers:**
```bash
# Basic influencer
python manage.py create_influencer "Full Name" "email@domain.com" "username"

# Full featured influencer
python manage.py create_influencer "Jane Smith" "jane@example.com" "janesmith" \
    --phone "+1987654321" \
    --instagram "janesmith_style" \
    --youtube "JaneSmithChannel" \
    --tiktok "janesmith" \
    --website "https://janesmith.com" \
    --commission 8.0 \
    --notes "Top fashion influencer with 500K followers"
```

### **Managing Influencers:**
- **Django Admin:** `http://127.0.0.1:8000/admin/`
- **View All:** `python manage.py create_influencer --list`
- **Update:** Use admin panel or create new command

---

## 📱 **SYSTEM FEATURES**

### **✅ What's Working:**
- ✅ Influencer authentication (username + API key)
- ✅ Direct dashboard access via shareable links
- ✅ Performance tracking dashboard
- ✅ Order listing and filtering
- ✅ Profile management
- ✅ Coupon code assignment
- ✅ Commission calculation
- ✅ Mobile-responsive design
- ✅ Secure logout functionality

### **🔧 Available Pages:**
1. **Info Page:** `/influencers/` - System overview
2. **Login Page:** `/influencers/login/` - Authentication
3. **Dashboard:** `/influencers/dashboard/` - Main stats
4. **Orders:** `/influencers/orders/` - Order tracking
5. **Profile:** `/influencers/profile/` - Personal info
6. **Logout:** `/influencers/logout/` - Sign out

---

## 🚦 **TESTING WORKFLOW**

### **For You (Testing):**
1. ✅ Visit: `http://127.0.0.1:8000/influencers/`
2. ✅ Click "Login to Dashboard" button
3. ✅ Use test credentials or direct link
4. ✅ Explore all dashboard features
5. ✅ Check orders, profile, and logout

### **For Future Influencers:**
1. ⏳ Admin creates their account
2. ✅ Admin provides username and API key
3. ✅ Influencer uses provided credentials to login
4. ✅ Influencer tracks their performance
5. ✅ Influencer gets paid based on commissions

---

## 🔗 **QUICK ACCESS LINKS**

| Purpose | URL |
|---------|-----|
| **Main System Page** | http://127.0.0.1:8000/influencers/ |
| **Login Page** | http://127.0.0.1:8000/influencers/login/ |
| **Test Dashboard** | http://127.0.0.1:8000/influencers/login/?username=johndoe&api_key=mXBsCGJHqsFo7ChNFffFihOrhjtGgPmpadp2bMZ81TSkD2KyAVj1hedVcw3hkNaR |
| **Admin Panel** | http://127.0.0.1:8000/admin/ |
| **Main Website** | http://127.0.0.1:8000/ |

---

## ⚡ **KEY POINTS:**

1. **No Self-Registration:** Influencers cannot register themselves
2. **Admin-Controlled:** All accounts created by administrators
3. **Secure Authentication:** Uses API keys instead of passwords
4. **Direct Access:** Shareable links for easy login
5. **Performance Tracking:** Real-time stats and commission tracking
6. **Mobile Friendly:** Works on all devices
7. **Integrated:** Works with existing Django e-commerce system

---

## 🎉 **READY TO USE!**

Your influencer system is **fully functional** and ready for production use. The test account `johndoe` is already set up with a coupon code, so you can immediately test all features.

**Start testing now:** http://127.0.0.1:8000/influencers/