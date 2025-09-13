import "./Diagram.css";

export default function ({ code }: { code: string }) {
  return (
    <div className="Diagram">
      <Error message="Traceback (most recent call last)" />
    </div>
  );
}

function Error({ message }: { message: string }) {
  return (
    <div className="Diagram-Error">
      <h2>Error</h2>
      <pre className="Diagram-Error-Traceback">{message}</pre>
    </div>
  );
}
