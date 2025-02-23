export default function Button({ text }: { text: string }) {
    return (
      <button className="bg-blue-500 text-white px-4 py-2 rounded-lg hover:bg-blue-600">
        {text}
      </button>
    );
  }
  