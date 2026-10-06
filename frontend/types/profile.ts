/**
 * User Profile Types (Person 3)
 */
export interface UserProfile {
  id: string;
  name: string;
  email: string;
  createdAt: string;
}

export interface UserProfileUpdateInput {
  name?: string;
  email?: string;
}
