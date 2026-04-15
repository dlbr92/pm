import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { LoginForm } from "@/components/LoginForm";

describe("LoginForm", () => {
  it("shows an error when credentials are invalid", async () => {
    const onLogin = vi.fn(() => false);
    render(<LoginForm onLogin={onLogin} />);

    await userEvent.type(screen.getByLabelText(/username/i), "bad-user");
    await userEvent.type(screen.getByLabelText(/password/i), "bad-pass");
    await userEvent.click(screen.getByRole("button", { name: /sign in/i }));

    expect(onLogin).toHaveBeenCalledWith("bad-user", "bad-pass");
    expect(screen.getByRole("alert")).toHaveTextContent(
      "Invalid username or password."
    );
  });

  it("submits clean username and clears error on success", async () => {
    const onLogin = vi
      .fn<(username: string, password: string) => boolean>()
      .mockReturnValueOnce(false)
      .mockReturnValueOnce(true);

    render(<LoginForm onLogin={onLogin} />);

    await userEvent.type(screen.getByLabelText(/username/i), " user ");
    await userEvent.type(screen.getByLabelText(/password/i), "password");
    await userEvent.click(screen.getByRole("button", { name: /sign in/i }));

    expect(screen.getByRole("alert")).toBeInTheDocument();

    await userEvent.click(screen.getByRole("button", { name: /sign in/i }));
    expect(onLogin).toHaveBeenLastCalledWith("user", "password");
    expect(screen.queryByRole("alert")).not.toBeInTheDocument();
  });
});
