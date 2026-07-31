# BlockHub
Explore blockchain wallets and transaction history across multiple networks.

#### Video Demo:
<YouTube link>

#### Description

BlockHub is a web app that lets you check any crypto wallet's balance and
recent activity without needing to know how to use a real block explorer.
You make an account, paste in a wallet address, pick a network (Ethereum,
BSC, Polygon, or Base), and it pulls up the balance and the last few
transactions for that wallet.

The idea came from how annoying it is to keep track of wallets across
different chains. Sites like Etherscan work fine, but they're built for
developers, they're chain-specific, and there's no way to save anything or
come back to it later unless you bookmark a bunch of separate URLs. I wanted
one place where I could search a wallet on any of the major chains and save
the ones I care about, tied to my own account, so I built that.

#### Features

- **Accounts** — you sign up with your name, a username, an email, and a
  password. Passwords are hashed before they touch the database, they're
  never stored as plain text.
- **Wallet search** — type in an address, pick a network, and get its
  balance plus its 10 most recent transactions, pulled live from the
  Covalent API.
- **Transaction page** — click any transaction from the list to see its own
  page with the hash, sender, receiver, value, status, block number, and gas
  used.
- **Favourites** — save a wallet you looked up so you don't have to
  re-search it later, and remove it whenever you want.
- **History + dashboard** — every search gets logged automatically, and your
  dashboard shows your last 5 favourites and last 5 searches as soon as you
  log in.
- **Profile page** — your account details plus how many searches and
  favourites you've racked up.
- **Light/dark mode** — a toggle in the navbar switches between light and
  dark themes, and your choice is saved in `localStorage` so it sticks the
  next time you open the site.

#### Technologies Used

- Python / Flask for the backend and routing
- Flask-Session for handling sessions
- SQLite for the database
- Werkzeug for password hashing
- Jinja2 for the HTML templates
- HTML/CSS/JavaScript on the frontend
- Requests, for calling the Covalent API
- python-dotenv, to keep the secret key and API key out of the code
- Covalent API, as the actual source of wallet/transaction data

#### Project Structure

- `app.py` — every route: home, register, login, logout, dashboard,
  profile, wallet search, adding/removing favourites, transaction detail.
- `helpers.py` — the login-required decorator, and `get_wallet_data()`,
  which does all the talking to the Covalent API and cleans up the response
  before it gets sent to the templates.
- `database/schema.sql` — the three tables: `users`, `search_history`,
  `favourites`.
- `templates/` — one HTML file per page, all extending `layout.html`.
- `static/css/style.css` and `static/js/script.js` — styling and any
  frontend interactivity.
- `requirements.txt` — the Python packages this needs.
- `.env` (not pushed to GitHub) — holds `SECRET_KEY` and `COVALENT_API_KEY`.

#### Database

BlockHub uses a SQLite database (`blockhub.db`) with three tables, defined
in `database/schema.sql`:

- **users** — id, name, username, email, password_hash, created_at. Usernames
  and emails are both marked `UNIQUE` so two accounts can't collide.
- **search_history** — id, user_id, wallet_address, network, searched_at.
  Each row is a logged wallet lookup, linked back to `users` through a
  foreign key.
- **favourites** — id, user_id, wallet_address, network, added_at. Same
  shape as `search_history`, but only holds wallets the user chose to save.

Keeping `search_history` and `favourites` as separate tables (instead of one
table with a "favourited" flag) made it easy to query and cap each one
independently, for example, only pulling the 5 most recent rows of each for
the dashboard.

#### How It Works

When you search a wallet, `/wallet` first logs the search to
`search_history`, then calls `get_wallet_data()` in `helpers.py`. That
function figures out which Covalent chain ID matches the network you picked,
grabs the native balance, then grabs the recent transactions. Some of those
transactions are token transfers instead of plain ETH/BNB/etc. sends, so if
the raw value comes back as zero, it digs into the transaction's log events
to pull the actual transferred amount instead of just showing 0.

Every page except home, login, and register is locked behind the
`login_required` decorator, so if you're not logged in you just get bounced
to `/login`. Sessions are stored on the server (filesystem-based, via
Flask-Session), and the key used to sign them comes from an environment
variable instead of being hardcoded, so it can be changed without touching
the code.

#### Design Decisions

I log the search before calling the API on purpose, not after. That way even
if the Covalent request fails or times out, the search still shows up in
your history, it reflects what you actually looked up, not just what
happened to load successfully.

For the transaction detail page, I went back and forth on how to pass the
data. I originally thought about stashing the transaction list in the
session so `/tx/<hash>` could just look it up locally, but ended up passing
the transaction's fields through the URL as query parameters instead, it's
simpler and doesn't depend on session state sticking around.

#### Challenges

The Covalent API was the hardest part of this project. The free tier's rate
limits kicked in more than I expected during testing, so I ended up adding
verbose logging around every request just to see what was actually failing
versus what was just getting throttled. I also underestimated how messy
on-chain data can be, a "transaction" isn't always a simple value transfer,
so figuring out how to detect and decode token transfer events (instead of
just reading the top-level `value` field) took a fair bit of trial and error
against real wallet addresses.

Getting sessions, the database, and the API calls to all agree with each
other was trickier than any one piece on its own. Deciding *when* to write
to `search_history` relative to the API call, for example, only became a
real question once I started testing with wallets that occasionally failed
to load.

#### Future Improvements

- Re-fetch transaction details from Covalent using the hash instead of
  trusting query parameters passed through the URL.
- Add CSRF protection to the login, register, and favourites forms.
- Add pagination to search history and favourites instead of hardcoding a
  limit of 5.
- Cache Covalent API responses briefly to cut down on redundant calls and
  stay further under the rate limit.
- Support more networks as Covalent adds them.

#### Getting Started

1. Install the dependencies:
   ```
   pip install -r requirements.txt
   ```
2. Make a `.env` file in the project root:
   ```
   SECRET_KEY=your-own-random-secret
   COVALENT_API_KEY=your-covalent-api-key
   ```
3. Set up the database:
   ```
   sqlite3 database/blockhub.db < database/schema.sql
   ```
4. Run it:
   ```
   flask run
   ```

#### Conclusion
Building BlockHub allowed me to combine concepts from across CS50, including Flask, SQL, authentication, sessions, API integration, and responsive web design. It also introduced me to the challenges of working with real-world blockchain data. The project represents the knowledge and skills I gained throughout CS50x and serves as a foundation for future blockchain-related applications.

#### Acknowledgements

Developed by Abdullah Farooq as the final project for CS50x. During development, I used AI tools to assist with debugging, refactoring, and improving documentation. The overall design, implementation, testing, and integration of the application are my own work.

CS50x Final Project – 2026
