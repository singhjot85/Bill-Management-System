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
export interface HomePageRow {
  cols: HomePageCol[];
  class?: string;
}

export interface HomePageCol {
  html: string;
  cols?: number | string;
  md?: number | string;
  class?: string;
}

export interface PRStubConfig {
  title?: string;
  description?: string;
  image?: string;
  icon?: string;
  class?: string;
}

export interface HomePageConfig {
  rows: HomePageRow[];
  topPRStubs: PRStubConfig[];
  bottomPRStubs: PRStubConfig[];
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
          url: '',
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
    rows: [
      {
        class: 'text-center mb-16',
        cols: [
          {
            md: 8,
            html: `
              <h1 class="text-h2 font-weight-black mb-6">
                Empowering Your <span class="text-primary">Financial Impact</span>
              </h1>
              <p class="text-h6 text-muted mb-10">
                Seamlessly manage your bills and support causes you care about, all in one modern platform.
              </p>
            `,
          },
        ],
      },
    ],
    topPRStubs: [
      {
        title: 'Our Mission',
        description: 'Helping communities through transparent bill management.',
        icon: 'mdi-earth',
      },
    ],
    bottomPRStubs: [
      {
        title: 'Get Involved',
        description: 'Join thousands of users making a difference every day.',
        icon: 'mdi-account-group',
      },
    ],
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
};
