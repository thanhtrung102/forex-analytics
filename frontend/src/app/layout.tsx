import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: 'Forex Analytics Dashboard',
  description: 'ML-powered forex market prediction and analytics platform',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="bg-gray-900 text-white antialiased">{children}</body>
    </html>
  );
}
