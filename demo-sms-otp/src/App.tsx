import SendCodeForm from "./components/send-code-form";
import ValidateCodeForm from "./components/validate-code-form";

function App() {
  return (
    <main className="container mx-auto my-20 space-y-12">
      <h1 className="text-center text-4xl font-bold">
        Bank Phone Verification
      </h1>
      <SendCodeForm />
      <ValidateCodeForm />
    </main>
  );
}

export default App;
