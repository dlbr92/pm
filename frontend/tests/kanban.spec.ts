import { expect, test, type Page } from "@playwright/test";
import { initialData, type BoardData } from "../src/lib/kanban";

const cloneBoard = (): BoardData => JSON.parse(JSON.stringify(initialData));

const mockBoardApi = async (page: Page) => {
  let board = cloneBoard();
  await page.route("**/api/board", async (route) => {
    const request = route.request();
    if (request.method() === "GET") {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify(board),
      });
      return;
    }

    if (request.method() === "PUT") {
      const payload = request.postDataJSON() as BoardData;
      board = payload;
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify(board),
      });
      return;
    }

    await route.fulfill({ status: 405 });
  });

  await page.route("**/api/ai/chat", async (route) => {
    const request = route.request();
    if (request.method() !== "POST") {
      await route.fulfill({ status: 405 });
      return;
    }

    const body = request.postDataJSON() as { message?: string };
    board = {
      ...board,
      columns: board.columns.map((column) =>
        column.id === "col-backlog" ? { ...column, title: "AI Backlog" } : column
      ),
    };
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({
        reply: body.message ? `AI handled: ${body.message}` : "AI handled",
        boardUpdated: true,
        board,
      }),
    });
  });
};

const login = async (page: Page) => {
  await page.getByLabel("Username").fill("user");
  await page.getByLabel("Password").fill("password");
  await page.getByRole("button", { name: /sign in/i }).click();
};

test("loads the kanban board", async ({ page }) => {
  await mockBoardApi(page);
  await page.goto("/");
  await expect(page.getByRole("heading", { name: /sign in/i })).toBeVisible();
  await login(page);
  await expect(page.getByRole("heading", { name: "Kanban Studio" })).toBeVisible();
  await expect(page.locator('[data-testid^="column-"]')).toHaveCount(5);
});

test("adds a card to a column", async ({ page }) => {
  await mockBoardApi(page);
  await page.goto("/");
  await login(page);
  const firstColumn = page.locator('[data-testid^="column-"]').first();
  await firstColumn.getByRole("button", { name: /add a card/i }).click();
  await firstColumn.getByPlaceholder("Card title").fill("Playwright card");
  await firstColumn.getByPlaceholder("Details").fill("Added via e2e.");
  await firstColumn.getByRole("button", { name: /add card/i }).click();
  await expect(firstColumn.getByText("Playwright card")).toBeVisible();
});

test("retains board changes after refresh", async ({ page }) => {
  await mockBoardApi(page);
  await page.goto("/");
  await login(page);
  const firstColumn = page.locator('[data-testid^="column-"]').first();
  const uniqueTitle = `Persist card ${Date.now()}`;

  await firstColumn.getByRole("button", { name: /add a card/i }).click();
  await firstColumn.getByPlaceholder("Card title").fill(uniqueTitle);
  await firstColumn.getByPlaceholder("Details").fill("Persistence smoke test.");
  await firstColumn.getByRole("button", { name: /add card/i }).click();
  await expect(firstColumn.getByText(uniqueTitle)).toBeVisible();

  await page.reload();
  const signInHeading = page.getByRole("heading", { name: /sign in/i });
  if (await signInHeading.isVisible()) {
    await login(page);
  }
  await expect(page.locator('[data-testid^="column-"]').first().getByText(uniqueTitle)).toBeVisible();
});

test("moves a card between columns", async ({ page }) => {
  await mockBoardApi(page);
  await page.goto("/");
  await login(page);
  const card = page.getByTestId("card-card-1");
  const targetColumn = page.getByTestId("column-col-review");
  const cardBox = await card.boundingBox();
  const columnBox = await targetColumn.boundingBox();
  if (!cardBox || !columnBox) {
    throw new Error("Unable to resolve drag coordinates.");
  }

  await page.mouse.move(
    cardBox.x + cardBox.width / 2,
    cardBox.y + cardBox.height / 2
  );
  await page.mouse.down();
  await page.mouse.move(
    columnBox.x + columnBox.width / 2,
    columnBox.y + 120,
    { steps: 12 }
  );
  await page.mouse.up();
  await expect(targetColumn.getByTestId("card-card-1")).toBeVisible();
});

test("requires login before board is visible", async ({ page }) => {
  await mockBoardApi(page);
  await page.goto("/");
  await expect(page.getByRole("heading", { name: /sign in/i })).toBeVisible();
  await expect(
    page.getByRole("heading", { name: /kanban studio/i })
  ).not.toBeVisible();
});

test("ai sidebar updates board immediately", async ({ page }) => {
  await mockBoardApi(page);
  await page.goto("/");
  await login(page);

  await page.getByLabel("AI message").fill("rename backlog");
  await page.getByRole("button", { name: /^send$/i }).click();

  await expect(page.getByText("AI handled: rename backlog")).toBeVisible();
  await expect(page.locator('input[aria-label="Column title"]').first()).toHaveValue(
    "AI Backlog"
  );
});
