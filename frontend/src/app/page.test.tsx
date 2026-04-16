import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import Home from "@/app/page";
import { AUTH_STORAGE_KEY } from "@/lib/auth";
import { initialData } from "@/lib/kanban";

const cloneBoard = () => JSON.parse(JSON.stringify(initialData));

const mockFetch = () => {
  const fetchMock = vi.fn((input: RequestInfo | URL, init?: RequestInit) => {
    const method = init?.method ?? "GET";

    if (typeof input === "string" && input === "/api/board" && method === "GET") {
      return Promise.resolve(
        new Response(JSON.stringify(cloneBoard()), {
          status: 200,
          headers: { "Content-Type": "application/json" },
        })
      );
    }

    if (typeof input === "string" && input === "/api/board" && method === "PUT") {
      return Promise.resolve(
        new Response(init?.body as string, {
          status: 200,
          headers: { "Content-Type": "application/json" },
        })
      );
    }

    return Promise.reject(new Error("Unexpected fetch call."));
  });

  vi.stubGlobal("fetch", fetchMock);
  return fetchMock;
};

describe("Home auth flow", () => {
  beforeAll(() => {
    mockFetch();
  });

  beforeEach(() => {
    window.sessionStorage.clear();
    vi.clearAllMocks();
    mockFetch();
  });

  afterAll(() => {
    vi.unstubAllGlobals();
  });

  it("shows login before authentication", () => {
    render(<Home />);
    expect(screen.getByRole("heading", { name: /sign in/i })).toBeInTheDocument();
    expect(
      screen.queryByRole("heading", { name: /kanban studio/i })
    ).not.toBeInTheDocument();
  });

  it("logs in with valid credentials and can log out", async () => {
    render(<Home />);

    await userEvent.type(screen.getByLabelText(/username/i), "user");
    await userEvent.type(screen.getByLabelText(/password/i), "password");
    await userEvent.click(screen.getByRole("button", { name: /sign in/i }));

    expect(
      await screen.findByRole("heading", { name: /kanban studio/i })
    ).toBeInTheDocument();
    expect(window.sessionStorage.getItem(AUTH_STORAGE_KEY)).toBe("true");

    await userEvent.click(screen.getByRole("button", { name: /log out/i }));
    expect(screen.getByRole("heading", { name: /sign in/i })).toBeInTheDocument();
    expect(window.sessionStorage.getItem(AUTH_STORAGE_KEY)).toBeNull();
  });

  it("rejects invalid credentials", async () => {
    render(<Home />);

    await userEvent.type(screen.getByLabelText(/username/i), "nope");
    await userEvent.type(screen.getByLabelText(/password/i), "wrong");
    await userEvent.click(screen.getByRole("button", { name: /sign in/i }));

    expect(screen.getByRole("alert")).toHaveTextContent(
      "Invalid username or password."
    );
    expect(
      screen.queryByRole("heading", { name: /kanban studio/i })
    ).not.toBeInTheDocument();
  });

  it("persists board changes to the backend API", async () => {
    const fetchSpy = mockFetch();
    render(<Home />);

    await userEvent.type(screen.getByLabelText(/username/i), "user");
    await userEvent.type(screen.getByLabelText(/password/i), "password");
    await userEvent.click(screen.getByRole("button", { name: /sign in/i }));
    expect(
      await screen.findByRole("heading", { name: /kanban studio/i })
    ).toBeInTheDocument();

    const firstColumn = screen.getAllByTestId(/column-/i)[0];
    const input = firstColumn.querySelector('input[aria-label="Column title"]');
    expect(input).toBeTruthy();
    await userEvent.clear(input as HTMLInputElement);
    await userEvent.type(input as HTMLInputElement, "Updated Backlog");

    const putCalls = fetchSpy.mock.calls.filter(
      ([url, init]) => url === "/api/board" && init?.method === "PUT"
    );
    expect(putCalls.length).toBeGreaterThan(0);
  });
});
