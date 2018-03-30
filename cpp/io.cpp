#include <iostream>
#include <fstream>
#include <sstream>
#include <unordered_map>
#include <vector>

#include "io.h"

using namespace std;

unordered_map<string, int> author_ids;
unordered_map<string, int> publication_ids;
vector<string> names;
vector<PubInfo> pub_infos;
vector<pair<int, int>> adj[MAXV];

string remove_quotes(const string &s) {
    string ret;
    for (auto c : s) {
        if (c != '\"') {
            ret += c;
        }
    }
    return ret;
}

void read_authors(const string &path) {
    ifstream fs(path + "authors.csv");
    string line;
    getline(fs, line);
    int idx = 0;
    while (getline(fs, line)) {
        string name = remove_quotes(line);
        names.push_back(name);
        author_ids[name] = idx;
        idx++;
    }
}

void read_publications(const string &path) {
    ifstream fs(path + "publications.csv");
    string line;
    getline(fs, line);
    int idx = 0;
    while (getline(fs, line)) {
        stringstream ss(line);

        string pub_id;
        getline(ss, pub_id, ',');
        pub_id = remove_quotes(pub_id);

        string pub_year;
        getline(ss, pub_year, ',');
        pub_year = remove_quotes(pub_year);

        publication_ids[pub_id] = idx;
        pub_infos.push_back(PubInfo(pub_id, stoi(pub_year)));
    }
}

void read_edges(string path, string file_name, int edge_type) {
    ifstream fs(path + file_name);
    string line;
    getline(fs, line);
    int idx = 0;
    while (getline(fs, line)) {
        stringstream ss(line);
        string from;
        getline(ss, from, ',');
        from = remove_quotes(from);
        int fromIdx = publication_ids[from];

        string to;
        getline(ss, to, ',');
        to = remove_quotes(to);
        int toIdx = publication_ids[to];

        adj[fromIdx].push_back({toIdx, edge_type});
    }
}
