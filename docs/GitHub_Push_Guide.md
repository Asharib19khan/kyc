# How to Push Your Project to GitHub

## 1. Initialize Git (If you haven't)
Open your terminal in the project folder and run:
```bash
git init
git add .
git commit -m "Final Build: KYC AI System"
```

## 2. Create Repository
1.  Go to [GitHub.com](https://github.com) and create a **New Repository**.
2.  Name it `KYC-Loan-System`.

## 3. Push Code
Copy the commands GitHub gives you, which look like this:
```bash
git remote add origin https://github.com/YOUR_USERNAME/KYC-Loan-System.git
git branch -M main
git push -u origin main
```

## 4. Deploy Landing Page to Vercel
1.  Go to [Vercel.com](https://vercel.com).
2.  Click **"Add New Project"**.
3.  Import your `KYC-Loan-System` repo.
4.  Vercel will automatically detect the `index.html` and deploy your marketing site!
