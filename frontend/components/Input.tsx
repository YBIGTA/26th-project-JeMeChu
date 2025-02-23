export default function Input({ placeholder }: { placeholder: string }) {
    return (
      <input 
        className="w-full p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
        placeholder={placeholder}
      />
    );
  }
  