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

export const defaultNavbarConfig: NavbarConfig = {
  leftItems: [
    {
      type: 'image',
      metadata: {
        url: '', // Will be populated from branding
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
        text: '', // Will be populated from branding
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
};
