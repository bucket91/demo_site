CREATE TABLE comments (
  id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  page TEXT NOT NULL,
  name TEXT NOT NULL,
  body TEXT NOT NULL,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_comments_page ON comments(page);

ALTER TABLE comments ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Anyone can read comments" ON comments
  FOR SELECT USING (true);

CREATE POLICY "Anyone can insert comments" ON comments
  FOR INSERT WITH CHECK (true);
