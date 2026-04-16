import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { AIChatSidebar } from "@/components/AIChatSidebar";

describe("AIChatSidebar", () => {
  it("renders conversation history", () => {
    render(
      <AIChatSidebar
        messages={[
          { role: "user", content: "Move card-1 to Review" },
          { role: "assistant", content: "Done. I moved it." },
        ]}
        isLoading={false}
        error={null}
        onSend={async () => {}}
      />
    );

    expect(screen.getByText("Move card-1 to Review")).toBeInTheDocument();
    expect(screen.getByText("Done. I moved it.")).toBeInTheDocument();
  });

  it("submits a new message", async () => {
    const onSend = vi.fn(async () => {});
    render(
      <AIChatSidebar messages={[]} isLoading={false} error={null} onSend={onSend} />
    );

    await userEvent.type(screen.getByLabelText(/ai message/i), "Create a new card");
    await userEvent.click(screen.getByRole("button", { name: /send/i }));

    expect(onSend).toHaveBeenCalledWith("Create a new card");
  });

  it("shows loading and error states", () => {
    render(
      <AIChatSidebar
        messages={[]}
        isLoading
        error="AI is unavailable."
        onSend={async () => {}}
      />
    );

    expect(screen.getByText("Thinking...")).toBeInTheDocument();
    expect(screen.getByRole("alert")).toHaveTextContent("AI is unavailable.");
  });
});
