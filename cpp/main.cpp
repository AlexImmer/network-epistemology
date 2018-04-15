#include <iostream>
#include <unordered_map>
#include <vector>
#include <fstream>
#include <sstream>
#include <queue>
#include <map>
#include <iomanip>

#include <boost/serialization/vector.hpp>
#include <boost/serialization/string.hpp>
#include <boost/serialization/unordered_map.hpp>
#include <boost/archive/binary_iarchive.hpp>
#include <boost/archive/binary_oarchive.hpp>


#include "io.h"

//#define SRLZ_GRAPH 1
//#define SRLZ_CCS 1
//#define WEIRD_PUBS 1

const int MIN_YEAR = 1936;
const int MAX_YEAR = 2018;

using namespace std;

bool visited[MAXV];
queue<int> bfsQueue;
vector<vector<int>> components;
vector<int> compID;

void bfsCC(int startIdx) {
    while (!bfsQueue.empty()) {
        bfsQueue.pop();
    }
    visited[startIdx] = true;
    for (bfsQueue.push(startIdx); !bfsQueue.empty(); bfsQueue.pop()) {
        int curr = bfsQueue.front();
        components.rbegin()->push_back(curr);
        compID[curr] = components.size() - 1;
        for (auto &nxt : adj[curr]) {
            if (!visited[nxt.next]) {
                visited[nxt.next] = true;
                bfsQueue.push(nxt.next);
            }
        }
    }
}

queue<int> q;
int dist[MAXV];
void bfs(const int &year, const int &EDGE_TYPE) {
    for (; !q.empty(); q.pop()) {
        int curr = q.front();
        for (auto x : adj[curr]) {
            if (x.type != EDGE_TYPE) {
                continue;
            }
            if (dist[x.next] != -1) {
                continue;
            }
            if (EDGE_TYPE == CITES && pub_infos[x.next].year >= year) {
                continue;
            }
            if (EDGE_TYPE == COLLABORATES && x.year >= year) {
                continue;
            }
            dist[x.next] = dist[curr] + 1;
            q.push(x.next);
        }
    }
}

template <typename Stream>
void reopen(Stream &ofs, const string &fileName)
{
    ofs.close();
    ofs.clear();
    ofs.open(fileName);
}

int main(int argc, char *argv[]) {
    string inPath = argv[1];
    string outPath = argv[2];
    ofstream ofs;
    ifstream ifs;

#ifdef SRLZ_GRAPH
    cerr << "Reading author file" << endl;
    read_authors(inPath);

    cerr << "Reading publication file" << endl;
    read_publications(inPath);

    cerr << "Reading coauthorship info" << endl;
    read_edges(inPath, "coauthorship.csv", COLLABORATES);

    cerr << "Reading citation data" << endl;
    read_edges(inPath, "citation.csv", CITES);

    cerr << "Reading authorship data" << endl;
    read_edges(inPath, "pub_auth.csv", PUBLISHES);

    reopen(ofs, inPath + "serialized.bak");
    boost::archive::binary_oarchive oa(ofs);
    oa << author_ids << publication_ids << names << pub_infos << adj << V;
    return 0;
#endif
    reopen(ifs, inPath + "serialized.bak");
    boost::archive::binary_iarchive ia(ifs);
    ia >> author_ids >> publication_ids >> names >> pub_infos >> adj >> V;
    cerr << "Graph successfully read" << endl;

#ifdef SRLZ_CCS
    compID.resize(V);
    for (int i = 0; i < V; i++) {
        if (!visited[i]) {
            components.push_back(vector<int>());
            bfsCC(i);
        }
    }
    reopen(ofs, inPath + "ccs.bak");
    boost::archive::binary_oarchive oarch(ofs);
    oarch << components << compID;
    return 0;
#endif
    reopen(ifs, inPath + "ccs.bak");
    boost::archive::binary_iarchive iaCC(ifs);
    iaCC >> components >> compID;
    cerr << "CCs successfully read" << endl;

#ifdef WEIRD_PUBS
    reopen(ofs, inPath + "weird_publications.txt");
    for (int i = 0; i < components.size(); i++) {
        vector<int> cc = components[i];
        if (cc.size() > 200) {
            cerr << i << endl;
            cerr << cc.size() << endl;
            continue;
        }
        for (auto v : cc) {
            if (v >= names.size()) {
                ofs << pub_infos[v].title << endl;
            }
        }
        ofs << "---------------------------------------------------------------------------------------------" << endl << endl;
    }
#endif


    // aliveness by transformation
    for (int year = MIN_YEAR; year <= MAX_YEAR; year++) {
        cerr << year << endl;
        while (!q.empty()) {
            q.pop();
        }
        memset(dist, -1, sizeof dist);
        for (auto pub : pub_infos) {
            int i = pub.first;
            if (pub.second.year == year) {
                dist[i] = 0;
                q.push(i);
            }
        }
        bfs(year, CITES);
        reopen(ofs, outPath +  "transformation" + to_string(year) + ".csv");
        ofs << "pub_id,distance" << endl;
        for (auto pub : pub_infos) {
            int i = pub.first;
            int dst = dist[i];
            if (dst <= 0) {
                continue;
            }
            ofs << pub.second.id << "," << dst << endl;
        }
    }


    // aliveness by tradition
    for (int year = MIN_YEAR; year <= MAX_YEAR; year++) {
        cerr << year << endl;
        while (!q.empty()) {
            q.pop();
        }
        memset(dist, -1, sizeof dist);
        for (auto pub : pub_infos) {
            int i = pub.first;
            if (pub.second.year == year) {
                for (auto x : adj[i]) {
                    if (x.type != AUTHORED) {
                        continue;
                    }
                    dist[x.next] = 0;
                    q.push(x.next);
                }
            }
        }
        bfs(year, COLLABORATES);
        reopen(ofs, outPath +  "tradition" + to_string(year) + ".csv");
        ofs << "pub_id,distance" << endl;
        for (auto author : names) {
            int i = author.first;
            int dst = dist[i];
            if (dst <= 0) {
                continue;
            }
            ofs << "\"" << author.second << "\"" << "," << dst << endl;
        }
    }
    return 0;
}