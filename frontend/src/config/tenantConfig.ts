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
export interface DonateHeroConfig {
  headline: string;
  subheadline: string;
  image: string;
  primaryCTA: { text: string; action: string };
  secondaryCTA: { text: string; url: string };
  trustBadges: { icon: string; text: string }[];
}

export interface DonateProblemConfig {
  headline: string;
  problemStatement: string;
  points: { icon: string; text: string }[];
  result: string;
  solutionQuote: string;
}

export interface DonationTier {
  name: string;
  amount: number;
  impact: string;
  bestFor: string;
  isMonthly?: boolean;
}

export interface DonationTiersConfig {
  headline: string;
  tiers: DonationTier[];
  inventoryStatus?: string;
}

export interface TransparencyStep {
  title: string;
  description: string;
}

export interface TransparencyConfig {
  headline: string;
  subheadline: string;
  steps: TransparencyStep[];
}

export interface RealTimeCounterItem {
  label: string;
  value: string | number;
}

export interface RealTimeCounterConfig {
  items: RealTimeCounterItem[];
  cta: { text: string; amount: number };
}

export interface FAQItem {
  question: string;
  answer: string;
}

export interface FAQConfig {
  items: FAQItem[];
}

export interface DonatePageConfig {
  hero: DonateHeroConfig;
  problem: DonateProblemConfig;
  tiers: DonationTiersConfig;
  recurringBlock: {
    headline: string;
    body: string;
    benefits: { icon: string; text: string }[];
    cta: string;
  };
  transparency: TransparencyConfig;
  socialProof: TestimonialsConfig;
  counter: RealTimeCounterConfig;
  faq: FAQConfig;
  finalCTA: {
    headline: string;
    subheadline: string;
    primaryCTA: string;
    secondaryCTA: string;
  };
  formTitle: string;
  formSubtitle: string;
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
    hero: {
      headline: 'Help Us Save a Life Today. ₹501 Feeds a Cow for a Week.',
      subheadline: 'Thousands of abandoned, injured, and starving cows depend on us. Your one-time or monthly donation provides food, shelter, and medical care. 100% of your donation is trackable via our app—you will receive a receipt and impact report instantly.',
      image: 'https://images.unsplash.com/photo-1546445317-29f4545e9d53?auto=format&fit=crop&q=80&w=2000',
      primaryCTA: { text: 'Donate Now – Feed a Cow', action: 'scrollToForm' },
      secondaryCTA: { text: 'Watch 2-min Video (Our Shelter)', url: '#' },
      trustBadges: [
        { icon: 'mdi-certificate', text: '80A & 12A Certified (Tax Exempt)' },
        { icon: 'mdi-trending-up', text: '₹1,500+ Raised This Month' },
        { icon: 'mdi-star', text: '4.9 Rated by Donors' }
      ]
    },
    problem: {
      headline: 'Every day, 3 stray cows in our city go hungry.',
      problemStatement: 'Dairy farms let go of old/non-lactating cows. Road accidents leave cows unable to graze. During dry seasons, there is no grass on the streets.',
      points: [
        { icon: 'mdi-home-alert', text: 'Abandonment: Dairy farms let go of old cows.' },
        { icon: 'mdi-ambulance', text: 'Injury: Road accidents leave cows unable to graze.' },
        { icon: 'mdi-food-off', text: 'Starvation: No grass on streets during dry seasons.' }
      ],
      result: 'Painful, slow starvation. We currently shelter 412 cows, but our food stock runs out every 10 days.',
      solutionQuote: 'You cannot rescue every cow, but you can feed one. Your donation buys hay, grain, and minerals for a specific cow in our shelter.'
    },
    tiers: {
      headline: 'Shop for Impact',
      tiers: [
        { name: 'One Full Meal', amount: 101, impact: 'Feeds 1 cow for 1 day', bestFor: 'Daily donors / Students' },
        { name: 'Weekly Care', amount: 501, impact: 'Feeds 1 cow for 7 days + 1 vitamin dose', bestFor: 'Working professionals' },
        { name: 'Medical Emergency', amount: 2500, impact: 'Covers wound treatment + antibiotics', bestFor: 'Animal lovers' },
        { name: 'Adopt a Cow', amount: 1500, impact: 'Name a cow. Monthly updates & photo.', bestFor: 'Families / Monthly givers', isMonthly: true },
        { name: 'Sponsor a Shelter', amount: 15000, impact: 'Feeds 30 cows for 1 week + plaque.', bestFor: 'Corporate CSR / HNIs' }
      ],
      inventoryStatus: 'Remaining meals for today: 142 / 500. Will you fill the gap?'
    },
    recurringBlock: {
      headline: 'Become a Monthly Guardian. Just ₹50/day = One cup of chai.',
      body: 'One-time donations save lives today. Monthly donations save lives forever.',
      benefits: [
        { icon: 'mdi-cow', text: 'Name your cow – Choose from our live herd list.' },
        { icon: 'mdi-camera', text: 'Photo update every month showing your cow eating/healthy.' },
        { icon: 'mdi-file-document-outline', text: 'Auto-tax receipt – Your app sends you a 80G certificate every April.' },
        { icon: 'mdi-pause-circle-outline', text: 'Pause anytime – No contracts. Cancel from your donor portal.' }
      ],
      cta: 'Become a Monthly Guardian (₹1,500/mo)'
    },
    transparency: {
      headline: 'No black box. Every rupee accounted for.',
      subheadline: 'Because your app is an invoicing tool, transparency is our superpower.',
      steps: [
        { title: 'Step 1', description: 'You donate via UPI/Card/Netbanking.' },
        { title: 'Step 2', description: 'Our app generates a tax invoice instantly (emailed + SMS).' },
        { title: 'Step 3', description: 'We purchase hay/medicines. Your app logs the bill (vendor name, date, amount).' },
        { title: 'Step 4', description: 'Log into your Donor Dashboard and see exactly where your money went.' }
      ]
    },
    socialProof: {
      items: [
        {
          quote: 'I donated ₹2,500 last month for a medical emergency. Within 24 hours, I got an invoice showing the vet bill and a photo. I\'ve never seen an NGO so transparent.',
          author: 'Priya M.',
          role: 'Donor from Bangalore'
        },
        {
          quote: 'The "adopt a cow" feature is beautiful. My son named her "Ganga". Every month we get a health report via email.',
          author: 'Rajesh K.',
          role: 'Donor from Delhi'
        }
      ]
    },
    counter: {
      items: [
        { label: 'Cows currently sheltered', value: 412 },
        { label: 'Meals needed today', value: 358 },
        { label: 'Meals funded (last 24 hrs)', value: 174 },
        { label: 'Left to fund', value: 184 }
      ],
      cta: { text: 'Donate a Meal', amount: 101 }
    },
    faq: {
      items: [
        { question: 'Is my donation tax-exempt?', answer: 'Yes. Under 80G (India) / 501(c)(3) (USA). You will get an instant receipt via our app.' },
        { question: 'Can I visit the shelter?', answer: 'Absolutely. Monthly donors get a free guided tour every Sunday.' },
        { icon: 'mdi-shield-check', question: 'How do I know my money is not stolen?', answer: 'Our app is a bill/invoice management system. Every single expense is logged as a bill.' },
        { question: 'What if I can only give ₹101?', answer: 'That feeds a cow for a full day. It is massive. Don\'t underestimate small amounts.' }
      ]
    },
    finalCTA: {
      headline: 'A hungry cow is waiting for you.',
      subheadline: 'For the cost of a pizza, you provide a week of safety, food, and love.',
      primaryCTA: 'Donate Now – Save a Life',
      secondaryCTA: 'Start a Monthly Gift (Get photos)'
    },
    formTitle: 'GauSeva Care Donation',
    formSubtitle: 'Your contribution directly saves lives.'
  },
};