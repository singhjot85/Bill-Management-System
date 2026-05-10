// Navbar Config
export interface NavbarItem {
  type: 'image' | 'text' | 'button' | 'icon-button' | 'spacer';
  metadata: {
    url?: string;
    text?: string;
    class?: string;
    icon?: string;
    to?: string;
    clickable?: boolean;
    variant?: string;
    size?: string;
    action?: string;
    width?: string | number;
    height?: string | number;
    iconResolver?: string;
    textResolver?: string;
  };
}

export interface NavbarConfig {
  leftItems: NavbarItem[];
  rightItems: NavbarItem[];
}

// Home Page Config
export interface HeroSectionConfig {
  headline: string;
  subheadline: string;
  primaryCTA: {
    text: string;
    to: string;
  };
}

export interface ProblemSolutionConfig {
  headline: string;
  problem: {
    title: string;
    items: string[];
  };
  solution: {
    title: string;
    items: {
      title: string;
      text: string;
    }[];
  };
}

export interface FeatureItem {
  icon: string;
  title: string;
  text: string;
}

export interface FeaturesGridConfig {
  features: FeatureItem[];
}

export interface UseCaseItem {
  title: string;
  quote: string;
  description: string;
}

export interface UseCasesConfig {
  items: UseCaseItem[];
}

export interface DashboardPeekConfig {
  image?: string;
  caption: string;
  widgets: {
    title: string;
    content: string;
  }[];
}

export interface TestimonialItem {
  quote: string;
  author: string;
  role: string;
}

export interface TestimonialsConfig {
  items: TestimonialItem[];
}

export interface PricingTier {
  name: string;
  price: string;
  popular?: boolean;
  features: string[];
}

export interface PricingConfig {
  tiers: PricingTier[];
}

export interface FinalCTAConfig {
  headline: string;
  subheadline: string;
  buttonText: string;
  finePrint: string;
}

export interface HomePageConfig {
  hero: HeroSectionConfig;
  problemSolution: ProblemSolutionConfig;
  featuresGrid: FeaturesGridConfig;
  useCases: UseCasesConfig;
  dashboardPeek: DashboardPeekConfig;
  testimonials: TestimonialsConfig;
  pricing: PricingConfig;
  finalCTA: FinalCTAConfig;
}

// Auth Page Config
export interface AuthPageConfig {
  left: {
    image: string;
    title: string;
    text: string;
    order: ('image' | 'title' | 'text')[];
  };
  header: {
    order: ('logo' | 'title')[];
  };
}

// Donate Page Config
export interface DonatePageConfig {
  topHtml?: string;
  bottomHtml?: string;
  leftImage?: string;
  rightImage?: string;
  backgroundImage?: string;
  formTitle?: string;
  formSubtitle?: string;
}

// Combined Tenant Config
export interface TenantViewConfig {
  navbar: NavbarConfig;
  home: HomePageConfig;
  auth: AuthPageConfig;
  donate: DonatePageConfig;
}

export const defaultTenantConfig: TenantViewConfig = {
  navbar: {
    leftItems: [
      {
        type: 'image',
        metadata: {
          url: 'src/assets/img/invoice-receipt-svgrepo-com.svg',
          width: 36,
          height: 36,
          class: 'mr-3',
          clickable: true,
          to: '/',
        },
      },
      {
        type: 'text',
        metadata: {
          textResolver: 'getTenantName',
          class: 'text-h6 font-weight-bold flex-shrink-0',
          clickable: true,
          to: '/',
        },
      },
    ],
    rightItems: [
      {
        type: 'icon-button',
        metadata: {
          iconResolver: 'getThemeIcon',
          action: 'toggleTheme',
          class: 'mr-2',
          size: 'small',
        },
      },
      {
        type: 'button',
        metadata: {
          text: 'Login/Signup',
          to: '/login',
          variant: 'text',
          class: 'text-none font-weight-bold rounded-lg px-4',
        },
      },
    ],
  },
  home: {
    hero: {
      headline: 'One Platform. Bills, Invoices, Donations & Stock. Zero Chaos.',
      subheadline: 'Stop juggling between accounting software, spreadsheets, and donation trackers. Automate your financial workflow from a single dashboard—whether you are billing a client, receipting a donor, or counting inventory.',
      primaryCTA: {
        text: 'Start Free Trial (No Credit Card Required)',
        to: '/donate'
      }
    },
    problemSolution: {
      headline: 'The nightmare of disconnected financial data ends here.',
      problem: {
        title: 'Problem',
        items: [
          'Manually entering invoices into Excel.',
          'Losing track of donation receipts during tax season.',
          'Selling products but not updating inventory counts.',
          'Late payment penalties on bills.'
        ]
      },
      solution: {
        title: 'Solution',
        items: [
          { title: 'Syncs instantly', text: 'Raise an invoice? Inventory drops automatically.' },
          { title: 'Donation ready', text: 'Generate tax-compliant receipts in 1-click.' },
          { title: 'Bill pay', text: 'Schedule vendor bills and avoid late fees.' },
          { title: 'Real-time P&L', text: 'See exactly how much you owe, are owed, and have in stock.' }
        ]
      }
    },
    featuresGrid: {
      features: [
        {
          icon: 'mdi-lightning-bolt',
          title: 'Smart Invoicing',
          text: 'Generate professional PDF invoices. Set recurring billing, auto-reminders, and track "Viewed/Paid" status.'
        },
        {
          icon: 'mdi-heart-handshake',
          title: 'Donation Management',
          text: 'Issue instant tax receipts. Track recurring pledges. Segment donors (One-time vs. Monthly) for thank-you emails.'
        },
        {
          icon: 'mdi-package-variant-closed',
          title: 'Inventory Sync',
          text: 'Low stock alerts. Barcode scanning. Automatically deduct inventory when a sales invoice is paid.'
        },
        {
          icon: 'mdi-calendar-clock',
          title: 'Bill/Expense Tracker',
          text: 'Snap a photo of a vendor bill. Set approval workflows. Schedule payments to avoid late fees.'
        }
      ]
    },
    useCases: {
      items: [
        {
          title: 'For Business Owners',
          quote: 'Stop writing "Out of Stock" emails.',
          description: 'When you sell a product via invoice, this app automatically reduces your inventory count. If stock is low, it alerts you before you over-sell.'
        },
        {
          title: 'For Non-Profits & Charities',
          quote: 'Donor trust starts with a clean receipt.',
          description: 'Generate IRS 501(c)(3) compliant donation receipts instantly. Track fundraising campaigns against goals. Send automated thank you notes.'
        },
        {
          title: 'For Freelancers & Agencies',
          quote: 'Get paid 3x faster.',
          description: 'Send branded invoices, accept credit cards/UPI, and enable "Pay Now" links. Automatic late-payment reminders mean you stop chasing clients.'
        }
      ]
    },
    dashboardPeek: {
      caption: 'Everything that matters. One screen.',
      widgets: [
        { title: 'Cash Flow', content: 'Graph showing incoming vs outgoing' },
        { title: 'At Risk Inventory', content: '3 units of Wireless Mouse left' },
        { title: 'Donation Goal', content: '75% funded for Q4 drive' }
      ]
    },
    testimonials: {
      items: [
        {
          quote: 'We used to have three different tools for donors, inventory, and invoices. FinTrack saved us $600/month and 20 hours of reconciliation work.',
          author: 'Sarah J.',
          role: 'Operations Director, Charity: Water'
        },
        {
          quote: 'The automatic inventory sync when I send an invoice is a game-changer. I used to oversell my handmade stock every Christmas. Not anymore.',
          author: 'Marcus T.',
          role: 'Etsy Seller & Woodworker'
        }
      ]
    },
    pricing: {
      tiers: [
        {
          name: 'Free Tier',
          price: '$0',
          features: ['5 invoices/month', '10 clients', 'Basic donation receipts', 'Manual inventory only']
        },
        {
          name: 'Pro Tier',
          price: '$29/month',
          popular: true,
          features: ['Unlimited invoices & bills', '500 inventory SKUs', 'Automatic stock sync', 'Donor segmentation', 'Bank reconciliation']
        },
        {
          name: 'Enterprise',
          price: 'Custom',
          features: ['Bulk SMS/Email', 'API access', 'Multi-location inventory', 'Dedicated account manager']
        }
      ]
    },
    finalCTA: {
      headline: 'Ready to replace three apps with one?',
      subheadline: 'Join 15,000+ businesses and non-profits managing bills, donations, and stock without the headache.',
      buttonText: 'Get Started for Free',
      finePrint: 'Includes free data migration from QuickBooks, Excel, or Stripe.'
    }
  },
  auth: {
    left: {
      image: 'https://illustrations.popsy.co/amber/waiting-for-the-mail.svg',
      title: 'Simplify Your Billing',
      text: 'Join thousands of users managing their finances and making an impact effortlessly.',
      order: ['image', 'title', 'text'],
    },
    header: {
      order: ['logo', 'title'],
    },
  },
  donate: {
    topHtml: '<div class="text-center mb-12"><h1 class="text-h2 font-weight-black mb-4">Support Our Cause</h1><p class="text-h6 text-muted">Your contribution helps us continue our mission.</p></div>',
    formTitle: 'Make a Donation',
    formSubtitle: 'Enter the amount you wish to contribute.',
    leftImage: 'https://www.shutterstock.com/image-photo/charity-financial-support-saving-concept-600nw-2136440783.jpg',
    bottomHtml: '<div class="text-center mt-12"><p class="text-caption text-muted">All donations are tax-deductible.</p></div>',
    // rightImage: 'https://drools.com/wp-content/uploads/2024/11/image-227.png',
  },
}