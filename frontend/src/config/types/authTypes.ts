export interface BadgeItem {
  text: string;
  icon?: string; // defaults to 'mdi-check'
}

export interface BrandSidebarConfig {
  badges: BadgeItem[];
}
