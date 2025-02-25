export interface Restaurant {
    id: string;
    name: string;
    category: string;
    address: string;
    rating: number;
    review_count: number;
    image_url?: string; // Optional
    photo_url: string | string[];
    menu: string | [string, number][];
    facilities: string | string[];
    seat_info: string | string[];
    distance?: string;
    business_hours?: string;
    connect_url?: string; // Link to external restaurant page
    reason?: string; // Why this restaurant was recommended
    core?: string; // Core keyword for highlighting
    parking?: string;
    phone?: string;
  }