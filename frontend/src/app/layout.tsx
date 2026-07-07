import './globals.css';

export const metadata = {
  title: 'Equil - The Finance Wizard',
  description: 'AI-powered financial advisory platform',
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className="antialiased min-h-screen bg-slate-900 text-slate-50">{children}</body>
    </html>
  );
}
