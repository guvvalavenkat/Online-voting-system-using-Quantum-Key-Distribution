-- Create the database and use it
CREATE DATABASE voting_system;
USE voting_system;

-- Create the voters table
CREATE TABLE voters (
    voter_id_number VARCHAR(255) PRIMARY KEY,
    name VARCHAR(255) NOT NULL
);

-- Create the votes table
CREATE TABLE votes (
    voter_id_number VARCHAR(255),
    encrypted_vote VARCHAR(255),
    qkd_key VARCHAR(255),
    PRIMARY KEY (voter_id_number),
    FOREIGN KEY (voter_id_number) REFERENCES voters(voter_id_number)
);

-- Create the admin table
CREATE TABLE admin (
    username VARCHAR(255) PRIMARY KEY,
    password VARCHAR(255) NOT NULL
);

-- Insert sample voters
INSERT INTO voters (voter_id_number, name) VALUES 
('VOTER123', 'John Doe'),
('VOTER124', 'Jane Smith');

-- Insert a sample admin
INSERT INTO admin (username, password) VALUES 
('admin', 'adminpassword');
