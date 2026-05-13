// ProfilePage — User profile with personal info, password change, and address management
import { usePerfil } from '@/entities/user';
import { ProfileInfo } from '@/features/profile/components/ProfileInfo';
import { PasswordChangeForm } from '@/features/profile/components/PasswordChangeForm';
import { AddressManager } from '@/features/profile/components/AddressManager';

export function ProfilePage() {
  const { isLoading } = usePerfil();

  // Full-page skeleton while initial profile data loads
  if (isLoading) {
    return (
      <div className="p-6 space-y-6 animate-pulse">
        <div className="h-8 bg-gray-200 rounded w-48 mb-6" />
        {[...Array(3)].map((_, i) => (
          <div key={i} className="bg-white rounded-lg shadow p-6 space-y-4">
            <div className="h-6 bg-gray-200 rounded w-40" />
            <div className="space-y-3">
              <div className="h-4 bg-gray-200 rounded w-full" />
              <div className="h-4 bg-gray-200 rounded w-3/4" />
              <div className="h-4 bg-gray-200 rounded w-1/2" />
            </div>
          </div>
        ))}
      </div>
    );
  }

  return (
    <div className="p-6 space-y-6">
      <h1 className="text-2xl font-bold text-gray-900">Mi Perfil</h1>

      <ProfileInfo />
      <PasswordChangeForm />
      <AddressManager />
    </div>
  );
}
