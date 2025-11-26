import React, { createContext, useContext, useState, useEffect } from 'react';

const LanguageContext = createContext();

const translations = {
  en: {
    // Navbar
    notifications: 'Notifications',
    logout: 'Logout',
    
    // Sidebar
    dashboard: 'Dashboard',
    loanManagement: 'Loan Management',
    myDocuments: 'My Documents',
    security: 'Security',
    settings: 'Settings',
    help: 'Help & Support',
    
    // Dashboard
    verificationInProgress: 'Verification In Progress',
    verificationMessage: 'Your account is currently under review. Our team is verifying your documents. This usually takes 24-48 hours.',
    accountCreated: 'Account Created',
    docsSubmitted: 'Docs Submitted',
    reviewing: 'Reviewing',
    
    verificationFailed: 'Verification Failed',
    verificationFailedMessage: 'Unfortunately, we could not verify your identity.',
    reason: 'Reason',
    reuploadDocuments: 'Re-upload Documents',
    
    accountStatus: 'Account Status',
    verifiedActive: 'Verified & Active',
    fullAccessUnlocked: 'Full Access Unlocked',
    
    loanApplication: 'Loan Application',
    noActiveLoan: 'No Active Loan',
    applyNow: 'Apply Now',
    approved: 'Approved',
    rejected: 'Rejected',
    pending: 'Pending',
    appliedOn: 'Applied on',
    
    trustScore: 'Trust Score',
    basedOnProfile: 'Based on your profile and history',
    
    personalDetails: 'Personal Details',
    fullName: 'Full Name',
    cnic: 'CNIC',
    email: 'Email',
    phone: 'Phone',
    address: 'Address',
    
    documents: 'Documents',
    
    applyForLoan: 'Apply for a Loan',
    instantApproval: 'Get instant approval based on your trust score.',
    loanAmount: 'Loan Amount (PKR)',
    monthlyIncome: 'Monthly Income',
    loanPurpose: 'Loan Purpose',
    selectPurpose: 'Select Purpose',
    personal: 'Personal Use',
    business: 'Business Expansion',
    education: 'Education',
    medical: 'Medical Emergency',
    home: 'Home Improvement',
    submitApplication: 'Submit Application',
    processing: 'Processing...',
    
    loanDetails: 'Loan Application Details',
    amount: 'Amount',
    purpose: 'Purpose',
    congratulations: 'Congratulations! Your Loan is Approved.',
    fundsReady: 'Your funds are ready for disbursement. Please download your approval letter below.',
    downloadApproval: 'Download Approval Letter',
    
    applicationRejected: 'Application Rejected',
    couldNotApprove: 'We could not approve your loan at this time.',
    downloadRejection: 'Download Rejection Notice',
    
    customerKey: 'Customer Key',
    useForSupport: 'Use this for support inquiries',
    copy: 'Copy',
    
    noNotifications: 'No notifications',
    darkMode: 'Dark Mode',
    language: 'Language',
  },
  ur: {
    // Navbar  
    notifications: 'اطلاعات',
    logout: 'لاگ آؤٹ',
    
    // Sidebar
    dashboard: 'ڈیش بورڈ',
    loanManagement: 'قرض کا انتظام',
    myDocuments: 'میرے دستاویزات',
    security: 'سیکیورٹی',
    settings: 'ترتیبات',
    help: 'مدد اور سپورٹ',
    
    // Dashboard
    verificationInProgress: 'تصدیق جاری ہے',
    verificationMessage: 'آپ کا اکاؤنٹ فی الحال زیر نظرثانی ہے۔ ہماری ٹیم آپ کی دستاویزات کی تصدیق کر رہی ہے۔ اس میں عام طور پر 24-48 گھنٹے لگتے ہیں۔',
    accountCreated: 'اکاؤنٹ بنایا گیا',
    docsSubmitted: 'دستاویزات جمع',
    reviewing: 'جائزہ لیا جا رہا ہے',
    
    verificationFailed: 'تصدیق ناکام',
    verificationFailedMessage: 'بدقسمتی سے، ہم آپ کی شناخت کی تصدیق نہیں کر سکے۔',
    reason: 'وجہ',
    reuploadDocuments: 'دستاویزات دوبارہ اپ لوڈ کریں',
    
    accountStatus: 'اکاؤنٹ کی حیثیت',
    verifiedActive: 'تصدیق شدہ اور فعال',
    fullAccessUnlocked: 'مکمل رسائی کھل گئی',
    
    loanApplication: 'قرض کی درخواست',
    noActiveLoan: 'کوئی فعال قرض نہیں',
    applyNow: 'ابھی درخواست دیں',
    approved: 'منظور شدہ',
    rejected: 'مسترد',
    pending: 'زیر التواء',
    appliedOn: 'درخواست کی تاریخ',
    
    trustScore: 'اعتماد سکور',
    basedOnProfile: 'آپ کی پروفائل اور تاریخ پر مبنی',
    
    personalDetails: 'ذاتی تفصیلات',
    fullName: 'پورا نام',
    cnic: 'شناختی کارڈ',
    email: 'ای میل',
    phone: 'فون',
    address: 'پتہ',
    
    documents: 'دستاویزات',
    
    applyForLoan: 'قرض کے لیے درخواست دیں',
    instantApproval: 'اپنے اعتماد سکور کی بنیاد پر فوری منظوری حاصل کریں۔',
    loanAmount: 'قرض کی رقم (روپے)',
    monthlyIncome: 'ماہانہ آمدنی',
    loanPurpose: 'قرض کا مقصد',
    selectPurpose: 'مقصد منتخب کریں',
    personal: 'ذاتی استعمال',
    business: 'کاروبار میں توسیع',
    education: 'تعلیم',
    medical: 'طبی ایمرجنسی',
    home: 'گھر کی بہتری',
    submitApplication: 'درخواست جمع کروائیں',
    processing: 'کارروائی جاری ہے...',
    
    loanDetails: 'قرض کی درخواست کی تفصیلات',
    amount: 'رقم',
    purpose: 'مقصد',
    congratulations: 'مبارک ہو! آپ کا قرض منظور ہو گیا۔',
    fundsReady: 'آپ کی رقم تقسیم کے لیے تیار ہے۔ براہ کرم نیچے اپنا منظوری خط ڈاؤن لوڈ کریں۔',
    downloadApproval: 'منظوری خط ڈاؤن لوڈ کریں',
    
    applicationRejected: 'درخواست مسترد',
    couldNotApprove: 'ہم اس وقت آپ کے قرض کی منظوری نہیں دے سکے۔',
    downloadRejection: 'مسترد نوٹس ڈاؤن لوڈ کریں',
    
    customerKey: 'کسٹمر کلید',
    useForSupport: 'سپورٹ کی پوچھ گچھ کے لیے استعمال کریں',
    copy: 'کاپی کریں',
    
    noNotifications: 'کوئی اطلاع نہیں',
    darkMode: 'ڈارک موڈ',
    language: 'زبان',
  }
};

export const LanguageProvider = ({ children }) => {
  const [language, setLanguage] = useState('en');

  useEffect(() => {
    const saved = localStorage.getItem('language');
    if (saved && (saved === 'en' || saved === 'ur')) {
      setLanguage(saved);
      document.documentElement.dir = saved === 'ur' ? 'rtl' : 'ltr';
      document.documentElement.lang = saved;
    }
  }, []);

  const toggleLanguage = () => {
    const newLang = language === 'en' ? 'ur' : 'en';
    setLanguage(newLang);
    localStorage.setItem('language', newLang);
    document.documentElement.dir = newLang === 'ur' ? 'rtl' : 'ltr';
    document.documentElement.lang = newLang;
  };

  const t = (key) => translations[language][key] || key;

  return (
    <LanguageContext.Provider value={{ language, toggleLanguage, t, isRTL: language === 'ur' }}>
      {children}
    </LanguageContext.Provider>
  );
};

export const useLanguage = () => {
  const context = useContext(LanguageContext);
  if (!context) throw new Error('useLanguage must be used within LanguageProvider');
  return context;
};
