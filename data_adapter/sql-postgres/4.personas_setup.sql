-- Create Persona Templates Table
CREATE TABLE persona_templates (
    id SERIAL PRIMARY KEY,
    uuid UUID NOT NULL DEFAULT uuid_generate_v4(),
    created_at TIMESTAMP NOT NULL DEFAULT now(),
    updated_at TIMESTAMP NOT NULL DEFAULT now(),
    is_deleted BOOLEAN NOT NULL DEFAULT FALSE,
    name VARCHAR(255) NOT NULL,
    description VARCHAR(255) NOT NULL,
    tone VARCHAR(255) NOT NULL,
    style VARCHAR(255) NOT NULL,
    instructions TEXT NOT NULL
);

-- Create Personas Table
CREATE TABLE personas (
    id SERIAL PRIMARY KEY,
    uuid UUID NOT NULL DEFAULT uuid_generate_v4(),
    created_at TIMESTAMP NOT NULL DEFAULT now(),
    updated_at TIMESTAMP NOT NULL DEFAULT now(),
    is_deleted BOOLEAN NOT NULL DEFAULT FALSE,
    name VARCHAR(255) NOT NULL,
    tone VARCHAR(255) NOT NULL,
    style VARCHAR(255) NOT NULL,
    instructions TEXT NOT NULL,
    personal_details TEXT NULL,
    user_id INTEGER NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE INDEX idx_personas_user_id ON personas(user_id);


-- Add persona templates
-- 1. Professional - formal and to the point
INSERT INTO persona_templates (name, description, tone, style, instructions) VALUES
('Professional', 'A persona for formal and concise communication.', 'Formal', 'To the point', 'Maintain a professional and objective tone. Focus on clear, direct communication without unnecessary embellishments. Use standard business language.');

-- 2. Friendly & Casual - Like a warm and approachable friend
INSERT INTO persona_templates (name, description, tone, style, instructions) VALUES
('Friendly & Casual', 'A persona that is warm, approachable, and informal.', 'Friendly', 'Conversational', 'Adopt a warm and approachable tone. Use casual language, contractions, and relatable examples. Aim to build rapport and sound like a helpful friend.');

-- 3. Witty & Playful - Fun, engaging and humourous
INSERT INTO persona_templates (name, description, tone, style, instructions) VALUES
('Witty & Playful', 'A persona that is fun, engaging, and incorporates humor.', 'Playful', 'Humorous and engaging', 'Inject humor, clever wordplay, and lightheartedness. Be engaging and entertaining, while still conveying the core message. Avoid overly serious or dry language.');
