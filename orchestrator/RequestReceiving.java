/*
RequestReceiving ONOS App by Jiakai Yu
 */

import java.io.IOException;
import java.util.regex.Matcher;
import java.util.regex.Pattern;
import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.io.PrintWriter;
import java.net.ServerSocket;
import java.net.Socket;

public class RequestReceiving {

    //Create a listener at port 8888
    public static void HTTPServer() {
        try {
            ServerSocket ss=new ServerSocket(8888);

            while(true){
                Socket socket=ss.accept();
                BufferedReader bd=new BufferedReader(new InputStreamReader(socket.getInputStream()));

                String requestHeader;
                int contentLength=0;
                while((requestHeader=bd.readLine())!=null&&!requestHeader.isEmpty()){

                    System.out.println(requestHeader);
                    if(requestHeader.startsWith("Content-Length")) {

                        //use Regular EXpression to get content length
                        String regEx="[^0-9]";
                        Pattern p = Pattern.compile(regEx);
                        String str= "\""+requestHeader+"\"";
                        Matcher m = p.matcher(str);
                        String num = m.replaceAll("").trim();
                        contentLength = Integer.parseInt(num);
                    }
                }

                StringBuffer sb=new StringBuffer();
                if(contentLength>0){
                    for (int i = 0; i < contentLength; i++) {
                        sb.append((char)bd.read());
                    }
                    System.out.println(sb.toString());
                }

                PrintWriter pw=new PrintWriter(socket.getOutputStream());
                pw.println("HTTP/1.1 200 OK");
                pw.println("Content-type:text/html");
                pw.println();
                pw.println("<h1>ok！</h1>");

                pw.flush();
                socket.close();
            }
        } catch (IOException e) {
            e.printStackTrace();
        }
    }




    public static void main(String[] args) {
        HTTPServer();
    }
}

